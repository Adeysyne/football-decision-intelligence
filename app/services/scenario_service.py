from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ScenarioRecord
from app.models.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)


def _to_response(
    record: ScenarioRecord,
) -> ScenarioResponse:
    return ScenarioResponse(
        scenario_id=record.scenario_id,
        status="validated",
        created_at=record.created_at,
        scenario=ScenarioCreate.model_validate(
            record.scenario_payload
        ),
        next_step="decision_engine",
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

    db.add(record)
    db.commit()
    db.refresh(record)

    return _to_response(
        record
    )


def get_scenario(
    scenario_id: UUID,
    db: Session,
) -> ScenarioResponse | None:
    record = db.get(
        ScenarioRecord,
        str(scenario_id),
    )

    if record is None:
        return None

    return _to_response(
        record
    )


def list_scenarios(
    db: Session,
    team_name: str | None = None,
    limit: int = 20,
) -> list[ScenarioResponse]:
    statement = select(
        ScenarioRecord
    )

    if team_name:
        statement = statement.where(
            ScenarioRecord.team_name
            == team_name
        )

    statement = (
        statement
        .order_by(
            ScenarioRecord.created_at.desc()
        )
        .limit(limit)
    )

    records = db.scalars(
        statement
    ).all()

    return [
        _to_response(record)
        for record in records
    ]