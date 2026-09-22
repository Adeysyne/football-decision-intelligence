from secrets import (
    compare_digest,
)

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.core.config import (
    get_settings,
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


def require_admin_access(
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

    if not compare_digest(
        supplied,
        expected,
    ):
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