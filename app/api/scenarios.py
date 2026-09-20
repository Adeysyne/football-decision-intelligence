from fastapi import (
    APIRouter,
    Depends,
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
)


router = APIRouter(
    prefix="/api/v1/scenarios",
    tags=["Scenarios"],
)


@router.post(
    "",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a tactical scenario",
    description=(
        "Validate and persist a football match situation "
        "for tactical decision analysis."
    ),
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