from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import ScenarioRecord
from app.models.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)


def create_scenario(
    scenario: ScenarioCreate,
    db: Session,
) -> ScenarioResponse:
    created_at = datetime.now(
        timezone.utc
    )

    record = ScenarioRecord(
        created_at=created_at,
        team_name=scenario.team_name,
        opponent_name=scenario.opponent_name,
        minute=scenario.minute,
        our_score=scenario.our_score,
        opponent_score=scenario.opponent_score,
        our_formation=scenario.our_formation,
        opponent_formation=(
            scenario.opponent_formation
        ),
        tactical_problem=(
            scenario.tactical_problem
        ),
        objective=scenario.objective,
        coach_observations=(
            scenario.coach_observations
        ),
        scenario_payload=(
            scenario.model_dump(
                mode="json"
            )
        ),
    )

    db.add(
        record
    )

    db.commit()

    db.refresh(
        record
    )

    return ScenarioResponse(
        scenario_id=record.scenario_id,
        status="validated",
        created_at=record.created_at,
        scenario=scenario,
        next_step="decision_engine",
    )