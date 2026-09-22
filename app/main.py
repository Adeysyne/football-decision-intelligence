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
from app.core.security import (
    security_limiter,
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
    docs_url=(
        None
        if settings.app_env
        == "production"
        else "/docs"
    ),
    redoc_url=(
        None
        if settings.app_env
        == "production"
        else "/redoc"
    ),
    openapi_url=(
        None
        if settings.app_env
        == "production"
        else "/openapi.json"
    ),
)


def _client_host(
    request: Request,
) -> str:
    if request.client is None:
        return "unknown"

    return (
        request.client.host
        or "unknown"
    )


def _security_headers(
    response,
) -> None:
    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "no-referrer"

    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )

    response.headers[
        "Cache-Control"
    ] = "no-store"

    if (
        settings.security_enable_hsts
    ):
        response.headers[
            "Strict-Transport-Security"
        ] = (
            "max-age=31536000; "
            "includeSubDomains"
        )


def _json_response(
    *,
    status_code: int,
    detail: str,
    request_id: str,
    retry_after: (
        int | None
    ) = None,
):
    response = JSONResponse(
        status_code=status_code,
        content={
            "detail": detail
        },
    )

    response.headers[
        "X-Request-ID"
    ] = request_id

    if retry_after is not None:
        response.headers[
            "Retry-After"
        ] = str(
            retry_after
        )

    _security_headers(
        response
    )

    return response


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
        client = _client_host(
            request
        )

        path = (
            request.url.path
        )

        protected_path = (
            path.startswith(
                "/api/v1"
            )
        )

        operations_path = (
            path.startswith(
                "/api/v1/operations"
            )
        )

        ai_path = (
            path.startswith(
                "/api/v1/ai"
            )
        )

        content_length = (
            request.headers.get(
                "content-length"
            )
        )

        if content_length:
            try:
                size = int(
                    content_length
                )

            except ValueError:
                size = 0

            if (
                size
                > settings.max_request_bytes
            ):
                status_code = 413

                return _json_response(
                    status_code=413,
                    detail=(
                        "Request payload "
                        "is too large."
                    ),
                    request_id=(
                        request_id
                    ),
                )

        if protected_path:
            api_key = (
                f"api:{client}"
            )

            api_allowed = (
                security_limiter.allow(
                    key=api_key,
                    limit=(
                        settings
                        .api_rate_limit_per_minute
                    ),
                    window_seconds=60,
                )
            )

            if not api_allowed:
                retry_after = (
                    security_limiter.retry_after(
                        key=api_key,
                        window_seconds=60,
                    )
                )

                status_code = 429

                return _json_response(
                    status_code=429,
                    detail=(
                        "API request limit "
                        "temporarily exceeded."
                    ),
                    request_id=(
                        request_id
                    ),
                    retry_after=(
                        retry_after
                    ),
                )

        if ai_path:
            ai_key = (
                f"ai:{client}"
            )

            ai_allowed = (
                security_limiter.allow(
                    key=ai_key,
                    limit=(
                        settings
                        .ai_rate_limit_per_minute
                    ),
                    window_seconds=60,
                )
            )

            if not ai_allowed:
                retry_after = (
                    security_limiter.retry_after(
                        key=ai_key,
                        window_seconds=60,
                    )
                )

                status_code = 429

                return _json_response(
                    status_code=429,
                    detail=(
                        "AI analysis request limit "
                        "temporarily exceeded."
                    ),
                    request_id=(
                        request_id
                    ),
                    retry_after=(
                        retry_after
                    ),
                )

        access_code = (
            settings
            .beta_access_code
            .strip()
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
                failure_key = (
                    f"beta-auth:{client}"
                )

                allowed = (
                    security_limiter.allow(
                        key=failure_key,
                        limit=(
                            settings
                            .access_failure_limit
                        ),
                        window_seconds=(
                            settings
                            .access_failure_window_seconds
                        ),
                    )
                )

                if not allowed:
                    retry_after = (
                        security_limiter
                        .retry_after(
                            key=failure_key,
                            window_seconds=(
                                settings
                                .access_failure_window_seconds
                            ),
                        )
                    )

                    status_code = 429

                    return _json_response(
                        status_code=429,
                        detail=(
                            "Too many private beta "
                            "access attempts."
                        ),
                        request_id=(
                            request_id
                        ),
                        retry_after=(
                            retry_after
                        ),
                    )

                status_code = 401

                return _json_response(
                    status_code=401,
                    detail=(
                        "Private beta access "
                        "code required."
                    ),
                    request_id=(
                        request_id
                    ),
                )

        response = await call_next(
            request
        )

        status_code = (
            response.status_code
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        _security_headers(
            response
        )

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