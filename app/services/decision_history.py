from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    DecisionRecord,
    ScenarioRecord,
)
from app.models.decision import DecisionBrief
from app.models.persistence import (
    PersistedDecisionResponse,
)
from app.models.scenario import ScenarioCreate
from app.services.decision_engine import (
    build_decision_brief,
)


def _to_response(
    record: DecisionRecord,
) -> PersistedDecisionResponse:
    return PersistedDecisionResponse(
        decision_id=record.decision_id,
        scenario_id=record.scenario_id,
        created_at=record.created_at,
        decision_brief=(
            DecisionBrief.model_validate(
                record.decision_payload
            )
        ),
    )


def analyse_and_persist_decision(
    scenario_id: UUID,
    db: Session,
) -> PersistedDecisionResponse | None:
    scenario_record = db.get(
        ScenarioRecord,
        str(scenario_id),
    )

    if scenario_record is None:
        return None

    scenario = ScenarioCreate.model_validate(
        scenario_record.scenario_payload
    )

    brief = build_decision_brief(
        scenario
    )

    record = DecisionRecord(
        scenario_id=str(
            scenario_id
        ),
        created_at=datetime.now(
            timezone.utc
        ),
        scenario_profile=(
            brief.scenario_profile
        ),
        leading_option_id=(
            brief.leading_option_id
        ),
        generated_from=(
            brief.generated_from
        ),
        decision_payload=(
            brief.model_dump(
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


def list_decisions(
    scenario_id: UUID,
    db: Session,
) -> list[PersistedDecisionResponse] | None:
    scenario_record = db.get(
        ScenarioRecord,
        str(scenario_id),
    )

    if scenario_record is None:
        return None

    statement = (
        select(DecisionRecord)
        .where(
            DecisionRecord.scenario_id
            == str(scenario_id)
        )
        .order_by(
            DecisionRecord.created_at.desc()
        )
    )

    records = db.scalars(
        statement
    ).all()

    return [
        _to_response(record)
        for record in records
    ]