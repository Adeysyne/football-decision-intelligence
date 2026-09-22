from secrets import (
    compare_digest,
)

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
    Request,
)
from sqlalchemy.orm import Session

from app.core.config import (
    get_settings,
)
from app.core.security import (
    security_limiter,
)
from app.db.database import (
    get_db,
)
from app.models.observability import (
    AIOperationsSummary,
)
from app.services.ai_observability import (
    get_ai_operations_summary,
)


router = APIRouter(
    prefix="/api/v1/operations",
    tags=[
        "Operations"
    ],
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


def require_admin_access(
    request: Request,
    x_admin_access_code: (
        str | None
    ) = Header(
        default=None,
        alias="X-Admin-Access-Code",
    ),
) -> None:
    settings = get_settings()

    expected = (
        settings.admin_access_code.strip()
    )

    if not expected:
        raise HTTPException(
            status_code=503,
            detail=(
                "Operations access is "
                "not configured."
            ),
        )

    supplied = (
        x_admin_access_code
        or ""
    )

    if compare_digest(
        supplied,
        expected,
    ):
        return

    client = _client_host(
        request
    )

    key = (
        f"admin-auth:{client}"
    )

    allowed = (
        security_limiter.allow(
            key=key,
            limit=(
                settings.access_failure_limit
            ),
            window_seconds=(
                settings
                .access_failure_window_seconds
            ),
        )
    )

    if not allowed:
        retry_after = (
            security_limiter.retry_after(
                key=key,
                window_seconds=(
                    settings
                    .access_failure_window_seconds
                ),
            )
        )

        raise HTTPException(
            status_code=429,
            detail=(
                "Too many administrator "
                "access attempts."
            ),
            headers={
                "Retry-After": str(
                    retry_after
                )
            },
        )

    raise HTTPException(
        status_code=401,
        detail=(
            "Admin access code required."
        ),
    )


@router.get(
    "/ai-summary",
    response_model=(
        AIOperationsSummary
    ),
    dependencies=[
        Depends(
            require_admin_access
        )
    ],
)
def ai_operations_summary(
    window_days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
    db: Session = Depends(
        get_db
    ),
) -> AIOperationsSummary:
    return get_ai_operations_summary(
        window_days=window_days,
        db=db,
    )