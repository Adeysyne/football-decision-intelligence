from datetime import (
    datetime,
    timezone,
)
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import (
    AIAnalysisRunRecord,
)
from app.models.observability import (
    AIAnalysisRunResponse,
)


def _response(
    record: AIAnalysisRunRecord,
) -> AIAnalysisRunResponse:
    return AIAnalysisRunResponse(
        analysis_run_id=(
            record.analysis_run_id
        ),
        started_at=record.started_at,
        completed_at=record.completed_at,
        team_name=record.team_name,
        model_name=record.model_name,
        status=record.status,
        latency_ms=record.latency_ms,
        verification_status=(
            record.verification_status
        ),
        revised=record.revised,
        review_attempt_count=(
            record.review_attempt_count
        ),
        input_tokens=record.input_tokens,
        output_tokens=record.output_tokens,
        total_tokens=record.total_tokens,
        estimated_cost_usd=(
            record.estimated_cost_usd
        ),
        error_type=record.error_type,
        error_message=record.error_message,
    )


def start_ai_analysis_run(
    *,
    team_name: str,
    model_name: str,
    db: Session,
) -> AIAnalysisRunResponse:
    record = AIAnalysisRunRecord(
        started_at=datetime.now(
            timezone.utc
        ),
        completed_at=None,
        team_name=team_name,
        model_name=model_name,
        status="started",
        latency_ms=None,
        verification_status=None,
        revised=False,
        review_attempt_count=0,
        input_tokens=None,
        output_tokens=None,
        total_tokens=None,
        estimated_cost_usd=None,
        error_type=None,
        error_message=None,
    )

    db.add(
        record
    )

    db.commit()

    db.refresh(
        record
    )

    return _response(
        record
    )


def complete_ai_analysis_run(
    *,
    analysis_run_id: UUID,
    status: str,
    verification_status: str | None,
    revised: bool,
    review_attempt_count: int,
    input_tokens: int | None,
    output_tokens: int | None,
    total_tokens: int | None,
    estimated_cost_usd: (
        float | None
    ),
    error_type: str | None,
    error_message: str | None,
    db: Session,
) -> AIAnalysisRunResponse:
    record = db.get(
        AIAnalysisRunRecord,
        str(
            analysis_run_id
        ),
    )

    if record is None:
        raise ValueError(
            "AI analysis run not found."
        )

    completed_at = datetime.now(
        timezone.utc
    )

    started_at = record.started_at

    if (
        started_at.tzinfo
        is None
    ):
        started_at = (
            started_at.replace(
                tzinfo=timezone.utc
            )
        )

    latency_ms = int(
        (
            completed_at
            - started_at
        ).total_seconds()
        * 1000
    )

    record.completed_at = (
        completed_at
    )

    record.status = status

    record.latency_ms = max(
        latency_ms,
        0,
    )

    record.verification_status = (
        verification_status
    )

    record.revised = revised

    record.review_attempt_count = (
        review_attempt_count
    )

    record.input_tokens = (
        input_tokens
    )

    record.output_tokens = (
        output_tokens
    )

    record.total_tokens = (
        total_tokens
    )

    record.estimated_cost_usd = (
        estimated_cost_usd
    )

    record.error_type = (
        error_type
    )

    record.error_message = (
        error_message
    )

    db.commit()

    db.refresh(
        record
    )

    return _response(
        record
    )


def get_ai_analysis_run(
    *,
    analysis_run_id: UUID,
    db: Session,
) -> AIAnalysisRunResponse | None:
    record = db.get(
        AIAnalysisRunRecord,
        str(
            analysis_run_id
        ),
    )

    if record is None:
        return None

    return _response(
        record
    )