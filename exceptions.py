from fastapi import HTTPException

class FinanceAPIError(HTTPException):
    """Base exception for all Finance API errors."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class TickerValidationError(FinanceAPIError):
    """Raised when ticker symbol validation fails."""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

class DataFetchError(FinanceAPIError):
    """Raised when there's an error fetching data from external sources."""
    def __init__(self, detail: str):
        super().__init__(status_code=503, detail=detail)

class RateLimitError(FinanceAPIError):
    """Raised when rate limits are exceeded."""
    def __init__(self, detail: str):
        super().__init__(status_code=429, detail=detail)

class InvalidDataError(FinanceAPIError):
    """Raised when received data is invalid or malformed."""
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)

class AuthenticationError(FinanceAPIError):
    """Raised when authentication fails."""
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail) 