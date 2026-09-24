from collections import Counter
from datetime import datetime, timezone
from typing import Any
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
    LatestCoachSelection,
    LatestDecisionOutcome,
    TeamHistorySummary,
    TeamLatestWorkflow,
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


def _scenario_payload(
    record: ScenarioRecord,
) -> dict[str, Any]:
    raw = (
        record.scenario_payload
        if isinstance(
            record.scenario_payload,
            dict,
        )
        else {}
    )

    nested = raw.get(
        "scenario"
    )

    if isinstance(
        nested,
        dict,
    ):
        payload = dict(
            nested
        )

    else:
        payload = dict(
            raw
        )

    payload.setdefault(
        "team_name",
        record.team_name,
    )

    payload.setdefault(
        "opponent_name",
        record.opponent_name,
    )

    payload.setdefault(
        "minute",
        record.minute,
    )

    payload.setdefault(
        "our_score",
        record.our_score,
    )

    payload.setdefault(
        "opponent_score",
        record.opponent_score,
    )

    payload.setdefault(
        "our_formation",
        record.our_formation,
    )

    payload.setdefault(
        "opponent_formation",
        record.opponent_formation,
    )

    payload.setdefault(
        "tactical_problem",
        record.tactical_problem,
    )

    payload.setdefault(
        "objective",
        record.objective,
    )

    payload.setdefault(
        "coach_observations",
        record.coach_observations,
    )

    payload.setdefault(
        "yellow_cards",
        [],
    )

    payload.setdefault(
        "red_cards",
        [],
    )

    payload.setdefault(
        "available_substitutions",
        [],
    )

    payload.setdefault(
        "options",
        [],
    )

    payload.setdefault(
        "requested_option_count",
        3,
    )

    return payload


def _decision_brief(
    record: DecisionRecord,
) -> dict[str, Any]:
    raw = (
        record.decision_payload
        if isinstance(
            record.decision_payload,
            dict,
        )
        else {}
    )

    nested = raw.get(
        "decision_brief"
    )

    if isinstance(
        nested,
        dict,
    ):
        return dict(
            nested
        )

    return dict(
        raw
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


def list_team_profiles(
    db: Session,
) -> list[TeamProfileResponse]:
    statement = (
        select(TeamRecord)
        .order_by(
            TeamRecord.team_name.asc()
        )
    )

    records = db.scalars(
        statement
    ).all()

    return [
        _profile_response(
            record
        )
        for record in records
    ]


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


def get_latest_team_workflow(
    team_id: UUID,
    db: Session,
) -> TeamLatestWorkflow | None:
    team = db.get(
        TeamRecord,
        str(team_id),
    )

    if team is None:
        raise TeamServiceError(
            "Team not found.",
            404,
        )

    scenario = db.scalar(
        select(
            ScenarioRecord
        )
        .where(
            ScenarioRecord.team_name
            == team.team_name
        )
        .order_by(
            ScenarioRecord.created_at.desc(),
            ScenarioRecord.scenario_id.desc(),
        )
        .limit(1)
    )

    if scenario is None:
        return None

    decision = db.scalar(
        select(
            DecisionRecord
        )
        .where(
            DecisionRecord.scenario_id
            == scenario.scenario_id
        )
        .order_by(
            DecisionRecord.created_at.desc(),
            DecisionRecord.decision_id.desc(),
        )
        .limit(1)
    )

    selection_record = None
    outcome_record = None

    if decision is not None:
        selection_record = db.scalar(
            select(
                CoachSelectionRecord
            ).where(
                CoachSelectionRecord.decision_id
                == decision.decision_id
            )
        )

        outcome_record = db.scalar(
            select(
                DecisionOutcomeRecord
            ).where(
                DecisionOutcomeRecord.decision_id
                == decision.decision_id
            )
        )

    selection = None

    if selection_record is not None:
        selection = LatestCoachSelection(
            selection_id=(
                selection_record.selection_id
            ),
            decision_id=(
                selection_record.decision_id
            ),
            selected_option_id=(
                selection_record.selected_option_id
            ),
            selected_at=(
                selection_record.selected_at
            ),
            rationale=(
                selection_record.rationale
            ),
        )

    outcome = None

    if outcome_record is not None:
        outcome = LatestDecisionOutcome(
            outcome_id=(
                outcome_record.outcome_id
            ),
            decision_id=(
                outcome_record.decision_id
            ),
            recorded_at=(
                outcome_record.recorded_at
            ),
            final_our_score=(
                outcome_record.final_our_score
            ),
            final_opponent_score=(
                outcome_record.final_opponent_score
            ),
            coach_assessment=(
                outcome_record.coach_assessment
            ),
            outcome_summary=(
                outcome_record.outcome_summary
            ),
            observed_effects=(
                outcome_record.observed_effects
                or []
            ),
            next_time_notes=(
                outcome_record.next_time_notes
            ),
        )

    return TeamLatestWorkflow(
        team_id=team.team_id,
        team_name=team.team_name,
        scenario_id=(
            scenario.scenario_id
        ),
        scenario_created_at=(
            scenario.created_at
        ),
        scenario=(
            _scenario_payload(
                scenario
            )
        ),
        decision_id=(
            decision.decision_id
            if decision is not None
            else None
        ),
        decision_created_at=(
            decision.created_at
            if decision is not None
            else None
        ),
        decision_brief=(
            _decision_brief(
                decision
            )
            if decision is not None
            else None
        ),
        selection=selection,
        outcome=outcome,
        is_complete=(
            outcome is not None
        ),
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