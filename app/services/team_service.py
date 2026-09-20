from collections import Counter
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    CoachSelectionRecord,
    DecisionOutcomeRecord,
    DecisionRecord,
    ScenarioRecord,
    TeamRecord,
)
from app.models.team import (
    TeamHistorySummary,
    TeamProfileCreate,
    TeamProfileResponse,
)


class TeamServiceError(
    RuntimeError
):
    def __init__(
        self,
        message: str,
        status_code: int,
    ):
        super().__init__(
            message
        )

        self.status_code = status_code


def _profile_response(
    record: TeamRecord,
) -> TeamProfileResponse:
    return TeamProfileResponse(
        team_id=record.team_id,
        team_name=record.team_name,
        created_at=record.created_at,
        updated_at=record.updated_at,
        default_formation=(
            record.default_formation
        ),
        tactical_identity=(
            record.tactical_identity
        ),
        notes=record.notes,
    )


def create_team_profile(
    profile: TeamProfileCreate,
    db: Session,
) -> TeamProfileResponse:
    existing = db.scalar(
        select(
            TeamRecord
        ).where(
            TeamRecord.team_name
            == profile.team_name
        )
    )

    if existing is not None:
        raise TeamServiceError(
            "A team profile with this name "
            "already exists.",
            409,
        )

    now = datetime.now(
        timezone.utc
    )

    record = TeamRecord(
        created_at=now,
        updated_at=now,
        team_name=profile.team_name,
        default_formation=(
            profile.default_formation
        ),
        tactical_identity=(
            profile.tactical_identity
        ),
        notes=profile.notes,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return _profile_response(
        record
    )


def get_team_profile(
    team_id: UUID,
    db: Session,
) -> TeamProfileResponse:
    record = db.get(
        TeamRecord,
        str(team_id),
    )

    if record is None:
        raise TeamServiceError(
            "Team not found.",
            404,
        )

    return _profile_response(
        record
    )


def get_team_history_summary(
    team_id: UUID,
    db: Session,
) -> TeamHistorySummary:
    team = db.get(
        TeamRecord,
        str(team_id),
    )

    if team is None:
        raise TeamServiceError(
            "Team not found.",
            404,
        )

    scenarios = db.scalars(
        select(
            ScenarioRecord
        ).where(
            ScenarioRecord.team_name
            == team.team_name
        )
    ).all()

    scenario_ids = [
        scenario.scenario_id
        for scenario in scenarios
    ]

    decisions = []

    if scenario_ids:
        decisions = db.scalars(
            select(
                DecisionRecord
            ).where(
                DecisionRecord.scenario_id.in_(
                    scenario_ids
                )
            )
        ).all()

    decision_ids = [
        decision.decision_id
        for decision in decisions
    ]

    selections = []
    outcomes = []

    if decision_ids:
        selections = db.scalars(
            select(
                CoachSelectionRecord
            ).where(
                CoachSelectionRecord.decision_id.in_(
                    decision_ids
                )
            )
        ).all()

        outcomes = db.scalars(
            select(
                DecisionOutcomeRecord
            ).where(
                DecisionOutcomeRecord.decision_id.in_(
                    decision_ids
                )
            )
        ).all()

    decision_lookup = {
        decision.decision_id: decision
        for decision in decisions
    }

    engine_leader_selected_count = sum(
        1
        for selection in selections
        if (
            selection.decision_id
            in decision_lookup
            and selection.selected_option_id
            == decision_lookup[
                selection.decision_id
            ].leading_option_id
        )
    )

    assessment_counter = Counter(
        outcome.coach_assessment
        for outcome in outcomes
    )

    assessment_counts = {
        "helped": assessment_counter[
            "helped"
        ],
        "neutral": assessment_counter[
            "neutral"
        ],
        "hurt": assessment_counter[
            "hurt"
        ],
        "unclear": assessment_counter[
            "unclear"
        ],
    }

    profile_counter = Counter(
        decision.scenario_profile
        for decision in decisions
    )

    scenario_profile_counts = {
        "protect_lead": profile_counter[
            "protect_lead"
        ],
        "chase_game": profile_counter[
            "chase_game"
        ],
        "control_game": profile_counter[
            "control_game"
        ],
        "balanced": profile_counter[
            "balanced"
        ],
    }

    return TeamHistorySummary(
        team_id=team.team_id,
        team_name=team.team_name,
        scenario_count=len(
            scenarios
        ),
        decision_count=len(
            decisions
        ),
        selection_count=len(
            selections
        ),
        outcome_count=len(
            outcomes
        ),
        engine_leader_selected_count=(
            engine_leader_selected_count
        ),
        assessment_counts=(
            assessment_counts
        ),
        scenario_profile_counts=(
            scenario_profile_counts
        ),
    )