from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.team import (
    TeamHistorySummary,
    TeamLatestWorkflow,
    TeamProfileCreate,
    TeamProfileResponse,
)
from app.services.team_service import (
    TeamServiceError,
    create_team_profile,
    get_latest_team_workflow,
    get_team_history_summary,
    get_team_profile,
    list_team_profiles,
)


router = APIRouter(
    prefix="/api/v1/teams",
    tags=["Teams"],
)


@router.post(
    "",
    response_model=TeamProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_team(
    profile: TeamProfileCreate,
    db: Session = Depends(
        get_db
    ),
) -> TeamProfileResponse:
    try:
        return create_team_profile(
            profile=profile,
            db=db,
        )

    except TeamServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None


@router.get(
    "",
    response_model=list[
        TeamProfileResponse
    ],
)
def teams(
    db: Session = Depends(
        get_db
    ),
) -> list[TeamProfileResponse]:
    return list_team_profiles(
        db=db
    )


@router.get(
    "/{team_id}/latest-workflow",
    response_model=(
        TeamLatestWorkflow | None
    ),
)
def latest_team_workflow(
    team_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> TeamLatestWorkflow | None:
    try:
        return get_latest_team_workflow(
            team_id=team_id,
            db=db,
        )

    except TeamServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None


@router.get(
    "/{team_id}/history-summary",
    response_model=TeamHistorySummary,
)
def team_history_summary(
    team_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> TeamHistorySummary:
    try:
        return get_team_history_summary(
            team_id=team_id,
            db=db,
        )

    except TeamServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None


@router.get(
    "/{team_id}",
    response_model=TeamProfileResponse,
)
def team_detail(
    team_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> TeamProfileResponse:
    try:
        return get_team_profile(
            team_id=team_id,
            db=db,
        )

    except TeamServiceError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None