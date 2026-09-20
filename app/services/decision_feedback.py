from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    CoachSelectionRecord,
    DecisionOutcomeRecord,
    DecisionRecord,
)
from app.models.persistence import (
    CoachSelectionCreate,
    CoachSelectionResponse,
    DecisionFeedbackResponse,
    DecisionOutcomeCreate,
    DecisionOutcomeResponse,
)


class DecisionFeedbackError(
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


def _selection_response(
    record: CoachSelectionRecord,
) -> CoachSelectionResponse:
    return CoachSelectionResponse(
        selection_id=record.selection_id,
        decision_id=record.decision_id,
        selected_option_id=(
            record.selected_option_id
        ),
        selected_at=record.selected_at,
        rationale=record.rationale,
    )


def _outcome_response(
    record: DecisionOutcomeRecord,
) -> DecisionOutcomeResponse:
    return DecisionOutcomeResponse(
        outcome_id=record.outcome_id,
        decision_id=record.decision_id,
        recorded_at=record.recorded_at,
        final_our_score=(
            record.final_our_score
        ),
        final_opponent_score=(
            record.final_opponent_score
        ),
        coach_assessment=(
            record.coach_assessment
        ),
        outcome_summary=(
            record.outcome_summary
        ),
        observed_effects=(
            record.observed_effects
        ),
        next_time_notes=(
            record.next_time_notes
        ),
    )


def record_coach_selection(
    decision_id: UUID,
    selection: CoachSelectionCreate,
    db: Session,
) -> CoachSelectionResponse:
    decision = db.get(
        DecisionRecord,
        str(decision_id),
    )

    if decision is None:
        raise DecisionFeedbackError(
            "Decision not found.",
            404,
        )

    existing = db.scalar(
        select(
            CoachSelectionRecord
        ).where(
            CoachSelectionRecord.decision_id
            == str(decision_id)
        )
    )

    if existing is not None:
        raise DecisionFeedbackError(
            "A coach selection has already "
            "been recorded for this decision.",
            409,
        )

    valid_option_ids = {
        item["option_id"]
        for item
        in decision.decision_payload[
            "options"
        ]
    }

    if (
        selection.selected_option_id
        not in valid_option_ids
    ):
        raise DecisionFeedbackError(
            "Selected option does not belong "
            "to this decision.",
            422,
        )

    record = CoachSelectionRecord(
        decision_id=str(
            decision_id
        ),
        selected_option_id=(
            selection.selected_option_id
        ),
        selected_at=datetime.now(
            timezone.utc
        ),
        rationale=selection.rationale,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return _selection_response(
        record
    )


def record_decision_outcome(
    decision_id: UUID,
    outcome: DecisionOutcomeCreate,
    db: Session,
) -> DecisionOutcomeResponse:
    decision = db.get(
        DecisionRecord,
        str(decision_id),
    )

    if decision is None:
        raise DecisionFeedbackError(
            "Decision not found.",
            404,
        )

    selection = db.scalar(
        select(
            CoachSelectionRecord
        ).where(
            CoachSelectionRecord.decision_id
            == str(decision_id)
        )
    )

    if selection is None:
        raise DecisionFeedbackError(
            "Record the coach's selected option "
            "before recording an outcome.",
            409,
        )

    existing = db.scalar(
        select(
            DecisionOutcomeRecord
        ).where(
            DecisionOutcomeRecord.decision_id
            == str(decision_id)
        )
    )

    if existing is not None:
        raise DecisionFeedbackError(
            "An outcome has already been "
            "recorded for this decision.",
            409,
        )

    record = DecisionOutcomeRecord(
        decision_id=str(
            decision_id
        ),
        recorded_at=datetime.now(
            timezone.utc
        ),
        final_our_score=(
            outcome.final_our_score
        ),
        final_opponent_score=(
            outcome.final_opponent_score
        ),
        coach_assessment=(
            outcome.coach_assessment
        ),
        outcome_summary=(
            outcome.outcome_summary
        ),
        observed_effects=(
            outcome.observed_effects
        ),
        next_time_notes=(
            outcome.next_time_notes
        ),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return _outcome_response(
        record
    )


def get_decision_feedback(
    decision_id: UUID,
    db: Session,
) -> DecisionFeedbackResponse:
    decision = db.get(
        DecisionRecord,
        str(decision_id),
    )

    if decision is None:
        raise DecisionFeedbackError(
            "Decision not found.",
            404,
        )

    selection_record = db.scalar(
        select(
            CoachSelectionRecord
        ).where(
            CoachSelectionRecord.decision_id
            == str(decision_id)
        )
    )

    outcome_record = db.scalar(
        select(
            DecisionOutcomeRecord
        ).where(
            DecisionOutcomeRecord.decision_id
            == str(decision_id)
        )
    )

    return DecisionFeedbackResponse(
        decision_id=decision_id,
        selection=(
            _selection_response(
                selection_record
            )
            if selection_record
            else None
        ),
        outcome=(
            _outcome_response(
                outcome_record
            )
            if outcome_record
            else None
        ),
    )