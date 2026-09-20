from fastapi import APIRouter, HTTPException

from app.models.scenario import ScenarioCreate
from app.services.ai_orchestration import (
    analyse_with_verification,
)
from app.services.ai_reasoning import (
    AIAnalysisError,
    analyse_with_ai,
)


router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI analysis"],
)


@router.post("/analyse")
def analyse_scenario(
    scenario: ScenarioCreate,
) -> dict:
    """
    Existing draft-analysis endpoint.

    Kept temporarily for backward compatibility while the
    verified pipeline is evaluated.
    """
    try:
        return analyse_with_ai(
            scenario
        )

    except AIAnalysisError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None


@router.post("/analyse-verified")
def analyse_verified_scenario(
    scenario: ScenarioCreate,
) -> dict:
    """
    Production-candidate pipeline:

    decision engine
        -> tactical retrieval
        -> AI reasoning
        -> critic
        -> optional controlled revision
        -> second critic
        -> verified response
    """
    try:
        return analyse_with_verification(
            scenario
        )

    except AIAnalysisError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None