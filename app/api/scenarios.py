from fastapi import APIRouter, status

from app.models.scenario import ScenarioCreate, ScenarioResponse
from app.services.scenario_service import create_scenario


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
        "Validate a football match situation and prepare it "
        "for tactical decision analysis."
    ),
)
def create_tactical_scenario(
    scenario: ScenarioCreate,
) -> ScenarioResponse:
    return create_scenario(scenario)