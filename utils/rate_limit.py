"""
In-memory sliding-window rate limiter.

Two windows are tracked per API key:
  - per-minute  (short burst limit)
  - per-day     (daily quota)

Thread safety: this is suitable for single-process deployments (SQLite / uvicorn
with one worker). For multi-process deployments, replace with a Redis-backed store.
"""
import time
from collections import defaultdict
from config import TIER_LIMITS


class RateLimitStore:
    def __init__(self) -> None:
        # api_key -> {"minute": [timestamps], "day": [timestamps]}
        self._store: dict = defaultdict(lambda: {"minute": [], "day": []})

    def check_and_record(self, api_key: str, tier: str) -> tuple[bool, dict]:
        """
        Check whether this request is within limits and record it if so.

        Returns (allowed, rate_info_dict).
        rate_info_dict always contains: limit, remaining, reset (Unix ts).
        On denial it also contains: exhausted_type ("minute" | "daily").
        """
        limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
        now = time.time()
        record = self._store[api_key]

        # Prune timestamps outside their window
        record["minute"] = [t for t in record["minute"] if now - t < 60]
        record["day"] = [t for t in record["day"] if now - t < 86_400]

        per_minute: int | None = limits["per_minute"]
        daily: int | None = limits["daily"]

        # Per-minute check
        if per_minute is not None and len(record["minute"]) >= per_minute:
            oldest = min(record["minute"])
            return False, {
                "limit": per_minute,
                "remaining": 0,
                "reset": int(oldest + 60),
                "exhausted_type": "minute",
            }

        # Daily check
        if daily is not None and len(record["day"]) >= daily:
            oldest = min(record["day"])
            return False, {
                "limit": daily,
                "remaining": 0,
                "reset": int(oldest + 86_400),
                "exhausted_type": "daily",
            }

        # Record this request
        record["minute"].append(now)
        record["day"].append(now)

        effective_limit = per_minute if per_minute is not None else 999_999
        remaining = (per_minute - len(record["minute"])) if per_minute is not None else 999_999

        return True, {
            "limit": effective_limit,
            "remaining": remaining,
            "reset": int(now + 60),
        }


rate_limit_store = RateLimitStore()
