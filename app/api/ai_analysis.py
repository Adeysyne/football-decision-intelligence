from fastapi import APIRouter, HTTPException

from app.models.scenario import ScenarioCreate
from app.services.ai_reasoning import (
    AIAnalysisError,
    analyse_with_ai,
)


router = APIRouter(
    prefix="/api/v1/ai",
    tags=["AI analysis"],
)


@router.post("/analyse")
def analyse_scenario(scenario: ScenarioCreate) -> dict:
    try:
        return analyse_with_ai(scenario)
    except AIAnalysisError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=str(exc),
        ) from None