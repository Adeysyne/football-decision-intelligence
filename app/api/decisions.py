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
    CoachSelectionCreate,
    CoachSelectionResponse,
    DecisionFeedbackResponse,
    DecisionOutcomeCreate,
    DecisionOutcomeResponse,
    PersistedDecisionResponse,
)
from app.models.scenario import ScenarioCreate
from app.services.decision_engine import (
    build_decision_brief,
)
from app.services.decision_feedback import (
    DecisionFeedbackError,
    get_decision_feedback,
    record_coach_selection,
    record_decision_outcome,
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


@router.post(
    "/{decision_id}/selection",
    response_model=CoachSelectionResponse,
)
def save_coach_selection(
    decision_id: UUID,
    selection: CoachSelectionCreate,
    db: Session = Depends(
        get_db
    ),
) -> CoachSelectionResponse:
    try:
        return record_coach_selection(
            decision_id=decision_id,
            selection=selection,
            db=db,
        )

    except DecisionFeedbackError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None


@router.post(
    "/{decision_id}/outcome",
    response_model=DecisionOutcomeResponse,
)
def save_decision_outcome(
    decision_id: UUID,
    outcome: DecisionOutcomeCreate,
    db: Session = Depends(
        get_db
    ),
) -> DecisionOutcomeResponse:
    try:
        return record_decision_outcome(
            decision_id=decision_id,
            outcome=outcome,
            db=db,
        )

    except DecisionFeedbackError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None


@router.get(
    "/{decision_id}/feedback",
    response_model=DecisionFeedbackResponse,
)
def decision_feedback(
    decision_id: UUID,
    db: Session = Depends(
        get_db
    ),
) -> DecisionFeedbackResponse:
    try:
        return get_decision_feedback(
            decision_id=decision_id,
            db=db,
        )

    except DecisionFeedbackError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None