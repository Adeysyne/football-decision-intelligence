from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.decision import DecisionBrief
from app.models.persistence import (
    PersistedDecisionResponse,
)
from app.models.scenario import ScenarioCreate
from app.services.decision_engine import (
    build_decision_brief,
)
from app.services.decision_history import (
    analyse_and_persist_decision,
    list_decisions,
)


router = APIRouter(
    prefix="/api/v1/decisions",
    tags=["Decisions"],
)


@router.post(
    "/analyse",
    response_model=DecisionBrief,
)
def analyse_tactical_scenario(
    scenario: ScenarioCreate,
) -> DecisionBrief:
    return build_decision_brief(
        scenario
    )


@router.post(
    "/scenarios/{scenario_id}/analyse",
    response_model=PersistedDecisionResponse,
)
def analyse_saved_scenario(
    scenario_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> PersistedDecisionResponse:
    result = analyse_and_persist_decision(
        scenario_id=scenario_id,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Scenario not found.",
        )

    return result


@router.get(
    "/scenarios/{scenario_id}",
    response_model=list[
        PersistedDecisionResponse
    ],
)
def decision_history(
    scenario_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> list[PersistedDecisionResponse]:
    result = list_decisions(
        scenario_id=scenario_id,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Scenario not found.",
        )

    return result