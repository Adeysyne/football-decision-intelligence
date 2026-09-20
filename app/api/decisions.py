from fastapi import APIRouter

from app.models.decision import DecisionBrief
from app.models.scenario import ScenarioCreate
from app.services.decision_engine import (
    build_decision_brief,
)


router = APIRouter(
    prefix="/api/v1/decisions",
    tags=["Decisions"],
)


@router.post(
    "/analyse",
    response_model=DecisionBrief,
    summary="Analyse a tactical scenario",
    description=(
        "Generate tactical alternatives and compare "
        "their trade-offs using the transparent V0.1 "
        "decision engine."
    ),
)
def analyse_tactical_scenario(
    scenario: ScenarioCreate,
) -> DecisionBrief:
    return build_decision_brief(
        scenario
    )