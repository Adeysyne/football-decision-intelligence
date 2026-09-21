from secrets import compare_digest

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.responses import (
    JSONResponse,
)

from app.api.ai_analysis import (
    router as ai_router,
)
from app.api.decisions import (
    router as decisions_router,
)
from app.api.pilot import (
    router as pilot_router,
)
from app.api.scenarios import (
    router as scenarios_router,
)
from app.api.teams import (
    router as teams_router,
)
from app.core.config import (
    get_settings,
)


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Low-data tactical decision support "
        "for football coaches."
    ),
)


@app.middleware(
    "http"
)
async def private_beta_access(
    request: Request,
    call_next,
):
    access_code = (
        settings.beta_access_code.strip()
    )

    protected_path = (
        request.url.path.startswith(
            "/api/v1"
        )
    )

    if (
        access_code
        and protected_path
    ):
        supplied_code = (
            request.headers.get(
                "X-Beta-Access-Code",
                "",
            )
        )

        if not compare_digest(
            supplied_code,
            access_code,
        ):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": (
                        "Private beta access "
                        "code required."
                    )
                },
            )

    return await call_next(
        request
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

app.include_router(
    pilot_router
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