"""
News API – main application entry point.

v1 endpoints:
  GET /v1/articles          Search & filter articles
  GET /v1/articles/{id}     Single article with related stubs
  GET /v1/headlines         Top headlines (last 24 h, cached 60 s)
  GET /v1/sources           Available news sources (cached 1 h)
  GET /v1/trending          Trending topics (cached 5 min)

Legacy endpoints (preserved for backwards compatibility):
  GET /api/news/{ticker}    Finance-focused news via Yahoo / Reuters / etc.

Management:
  POST /users/register      Self-serve API key generation
  GET  /admin/              Admin dashboard (HTTP Basic Auth)
"""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, get_db
from routers import admin, users
from routers.v1 import articles, headlines, sources, trending
from services.news_aggregator import refresh_articles, seed_sources


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create / migrate tables
    Base.metadata.create_all(bind=engine)

    # Seed sources and do an initial article fetch
    db = next(get_db())
    try:
        seed_sources(db)
        await refresh_articles(db)
    finally:
        db.close()

    yield


_DESCRIPTION = """
## News API

A RESTful service that aggregates, indexes, and serves news articles from
multiple publishers.

### Authentication

All `/v1/*` endpoints require an API key supplied via:

* **Header** (preferred): `X-Api-Key: YOUR_KEY`
* **Query param**: `?apiKey=YOUR_KEY`

Register for a free key at `POST /users/register`.

### Rate limits

| Tier       | Requests / day | Requests / min | History |
|------------|---------------:|---------------:|---------|
| Free       | 1,000          | 10             | 30 days |
| Developer  | 10,000         | 60             | 1 year  |
| Business   | 100,000        | 300            | Full    |
| Enterprise | Unlimited      | Custom         | Full    |

Rate-limit status is returned in every response via the
`X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers.

### Caching

| Endpoint       | TTL     |
|----------------|---------|
| `/v1/headlines` | 60 s   |
| `/v1/articles`  | 5 min  |
| `/v1/sources`   | 1 h    |
| `/v1/trending`  | 5 min  |
"""

app = FastAPI(
    title="News API",
    description=_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "API Support",
        "url": "https://github.com/Khanalpratyush",
        "email": "pratyushkhanal95@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── v1 API routes ─────────────────────────────────────────────────────────────

app.include_router(articles.router, prefix="/v1")
app.include_router(headlines.router, prefix="/v1")
app.include_router(sources.router,   prefix="/v1")
app.include_router(trending.router,  prefix="/v1")

# ── Management routes ─────────────────────────────────────────────────────────

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["root"], response_model=dict[str, Any])
async def root() -> dict:
    return {
        "name": "News API",
        "version": "1.0.0",
        "documentation": {"swagger_ui": "/docs", "redoc": "/redoc"},
        "endpoints": {
            "articles":  "/v1/articles",
            "headlines": "/v1/headlines",
            "sources":   "/v1/sources",
            "trending":  "/v1/trending",
            "register":  "/users/register",
        },
        "authentication": {
            "header": "X-Api-Key",
            "query_param": "apiKey",
        },
    }
