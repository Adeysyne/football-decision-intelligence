from fastapi import (
    APIRouter,
    Depends,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.pilot import (
    PilotInterestCreate,
    PilotInterestResponse,
)
from app.services.pilot_service import (
    record_pilot_interest,
)


router = APIRouter(
    prefix="/api/v1/pilot-interest",
    tags=[
        "Private beta"
    ],
)


@router.post(
    "",
    response_model=PilotInterestResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_pilot_interest(
    interest: PilotInterestCreate,
    db: Session = Depends(
        get_db
    ),
) -> PilotInterestResponse:
    return record_pilot_interest(
        interest=interest,
        db=db,
    )