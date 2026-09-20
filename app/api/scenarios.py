from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)
from app.services.scenario_service import (
    create_scenario,
    get_scenario,
    list_scenarios,
)


router = APIRouter(
    prefix="/api/v1/scenarios",
    tags=["Scenarios"],
)


@router.post(
    "",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tactical_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(
        get_db
    ),
) -> ScenarioResponse:
    return create_scenario(
        scenario=scenario,
        db=db,
    )


@router.get(
    "",
    response_model=list[
        ScenarioResponse
    ],
)
def scenario_history(
    team_name: str | None = None,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(
        get_db
    ),
) -> list[ScenarioResponse]:
    return list_scenarios(
        db=db,
        team_name=team_name,
        limit=limit,
    )


@router.get(
    "/{scenario_id}",
    response_model=ScenarioResponse,
)
def scenario_detail(
    scenario_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> ScenarioResponse:
    result = get_scenario(
        scenario_id=scenario_id,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Scenario not found.",
        )

    return result