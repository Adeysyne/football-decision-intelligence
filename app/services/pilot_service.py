from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import (
    PilotInterestRecord,
)
from app.models.pilot import (
    PilotInterestCreate,
    PilotInterestResponse,
)


def record_pilot_interest(
    interest: PilotInterestCreate,
    db: Session,
) -> PilotInterestResponse:
    record = PilotInterestRecord(
        created_at=datetime.now(
            timezone.utc
        ),
        coach_name=interest.coach_name,
        email=interest.email,
        club_or_team=(
            interest.club_or_team
        ),
        role=interest.role,
        would_use_in_real_matches=(
            interest.would_use_in_real_matches
        ),
        join_private_pilot=(
            interest.join_private_pilot
        ),
        willingness_to_pay_monthly_gbp=(
            interest.willingness_to_pay_monthly_gbp
        ),
        most_valuable_feature=(
            interest.most_valuable_feature
        ),
        feedback=interest.feedback,
    )

    db.add(
        record
    )

    db.commit()

    db.refresh(
        record
    )

    return PilotInterestResponse(
        pilot_interest_id=(
            record.pilot_interest_id
        ),
        created_at=record.created_at,
        coach_name=record.coach_name,
        email=record.email,
        club_or_team=(
            record.club_or_team
        ),
        role=record.role,
        would_use_in_real_matches=(
            record.would_use_in_real_matches
        ),
        join_private_pilot=(
            record.join_private_pilot
        ),
        willingness_to_pay_monthly_gbp=(
            record.willingness_to_pay_monthly_gbp
        ),
        most_valuable_feature=(
            record.most_valuable_feature
        ),
        feedback=record.feedback,
    )