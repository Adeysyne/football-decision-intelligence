from fastapi import FastAPI

from app.api.ai_analysis import (
    router as ai_router,
)
from app.api.decisions import (
    router as decisions_router,
)
from app.api.scenarios import (
    router as scenarios_router,
)
from app.api.teams import (
    router as teams_router,
)
from app.core.config import get_settings


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Low-data tactical decision support "
        "for football coaches."
    ),
)


app.include_router(
    scenarios_router
)

app.include_router(
    decisions_router
)

app.include_router(
    ai_router
)

app.include_router(
    teams_router
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "product": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }