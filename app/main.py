import logging
import time
from secrets import (
    compare_digest,
)
from uuid import uuid4

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
from app.api.operations import (
    router as operations_router,
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
from app.core.logging_config import (
    configure_logging,
)
from app.core.request_context import (
    reset_request_id,
    set_request_id,
)


configure_logging()


logger = logging.getLogger(
    "fdi.request"
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
async def request_pipeline(
    request: Request,
    call_next,
):
    request_id = str(
        uuid4()
    )

    token = set_request_id(
        request_id
    )

    started = (
        time.perf_counter()
    )

    status_code = 500

    try:
        access_code = (
            settings.beta_access_code.strip()
        )

        protected_path = (
            request.url.path.startswith(
                "/api/v1"
            )
        )

        operations_path = (
            request.url.path.startswith(
                "/api/v1/operations"
            )
        )

        if (
            access_code
            and protected_path
            and not operations_path
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
                response = JSONResponse(
                    status_code=401,
                    content={
                        "detail": (
                            "Private beta access "
                            "code required."
                        )
                    },
                )

                status_code = 401

                response.headers[
                    "X-Request-ID"
                ] = request_id

                return response

        response = await call_next(
            request
        )

        status_code = (
            response.status_code
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response

    except Exception as exc:
        logger.error(
            "request_failed",
            extra={
                "event": (
                    "request_failed"
                ),
                "request_id": (
                    request_id
                ),
                "method": (
                    request.method
                ),
                "path": (
                    request.url.path
                ),
                "status_code": 500,
                "error_type": (
                    type(
                        exc
                    ).__name__
                ),
            },
        )

        raise

    finally:
        latency_ms = round(
            (
                time.perf_counter()
                - started
            )
            * 1000,
            2,
        )

        if (
            request.url.path
            != "/health"
        ):
            logger.info(
                "request_completed",
                extra={
                    "event": (
                        "request_completed"
                    ),
                    "request_id": (
                        request_id
                    ),
                    "method": (
                        request.method
                    ),
                    "path": (
                        request.url.path
                    ),
                    "status_code": (
                        status_code
                    ),
                    "latency_ms": (
                        latency_ms
                    ),
                },
            )

        reset_request_id(
            token
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

app.include_router(
    operations_router
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "product": (
            settings.app_name
        ),
        "version": (
            settings.app_version
        ),
        "environment": (
            settings.app_env
        ),
        "status": "running",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }