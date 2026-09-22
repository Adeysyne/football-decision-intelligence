from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import UUID

from sqlalchemy import (
    select,
)
from sqlalchemy.orm import Session

from app.db.models import (
    AIAnalysisRunRecord,
)
from app.models.observability import (
    AIAnalysisRunResponse,
    AIAnalysisRunSummaryItem,
    AIOperationsSummary,
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


def summarize_usage(
    usage_by_stage: dict | None,
) -> dict[str, int | None]:
    if not isinstance(
        usage_by_stage,
        dict,
    ):
        return {
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }

    input_total = 0
    output_total = 0
    explicit_total = 0

    input_found = False
    output_found = False
    total_found = False

    for stage_usage in (
        usage_by_stage.values()
    ):
        if stage_usage is None:
            continue

        if hasattr(
            stage_usage,
            "model_dump",
        ):
            stage_usage = (
                stage_usage.model_dump()
            )

        if not isinstance(
            stage_usage,
            dict,
        ):
            continue

        input_tokens = (
            stage_usage.get(
                "input_tokens"
            )
        )

        output_tokens = (
            stage_usage.get(
                "output_tokens"
            )
        )

        total_tokens = (
            stage_usage.get(
                "total_tokens"
            )
        )

        if isinstance(
            input_tokens,
            int,
        ):
            input_total += (
                input_tokens
            )
            input_found = True

        if isinstance(
            output_tokens,
            int,
        ):
            output_total += (
                output_tokens
            )
            output_found = True

        if isinstance(
            total_tokens,
            int,
        ):
            explicit_total += (
                total_tokens
            )
            total_found = True

    if total_found:
        combined_total = (
            explicit_total
        )

    elif (
        input_found
        or output_found
    ):
        combined_total = (
            input_total
            + output_total
        )

    else:
        combined_total = None

    return {
        "input_tokens": (
            input_total
            if input_found
            else None
        ),
        "output_tokens": (
            output_total
            if output_found
            else None
        ),
        "total_tokens": (
            combined_total
        ),
    }


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


def _percentage(
    numerator: int,
    denominator: int,
) -> float:
    if denominator <= 0:
        return 0.0

    return round(
        (
            numerator
            / denominator
        )
        * 100,
        2,
    )


def get_ai_operations_summary(
    *,
    window_days: int,
    db: Session,
) -> AIOperationsSummary:
    since = (
        datetime.now(
            timezone.utc
        )
        - timedelta(
            days=window_days
        )
    )

    records = list(
        db.scalars(
            select(
                AIAnalysisRunRecord
            )
            .where(
                AIAnalysisRunRecord.started_at
                >= since
            )
            .order_by(
                AIAnalysisRunRecord.started_at.desc()
            )
        ).all()
    )

    total_runs = len(
        records
    )

    approved_runs = sum(
        1
        for item in records
        if item.status
        == "approved"
    )

    verification_failed_runs = sum(
        1
        for item in records
        if item.status
        == "verification_failed"
    )

    provider_failed_runs = sum(
        1
        for item in records
        if item.status
        == "provider_failed"
    )

    failed_runs = sum(
        1
        for item in records
        if item.status
        == "failed"
    )

    in_progress_runs = sum(
        1
        for item in records
        if item.status
        == "started"
    )

    revised_runs = sum(
        1
        for item in records
        if item.revised
    )

    completed_runs = [
        item
        for item in records
        if item.status
        != "started"
    ]

    latency_values = [
        item.latency_ms
        for item in completed_runs
        if item.latency_ms
        is not None
    ]

    if latency_values:
        average_latency_ms = round(
            sum(
                latency_values
            )
            / len(
                latency_values
            ),
            2,
        )

    else:
        average_latency_ms = None

    input_tokens = sum(
        item.input_tokens
        or 0
        for item in records
    )

    output_tokens = sum(
        item.output_tokens
        or 0
        for item in records
    )

    total_tokens = sum(
        item.total_tokens
        or 0
        for item in records
    )

    estimated_cost_usd = round(
        sum(
            item.estimated_cost_usd
            or 0.0
            for item in records
        ),
        6,
    )

    model_counts: dict[
        str,
        int,
    ] = {}

    for item in records:
        model_counts[
            item.model_name
        ] = (
            model_counts.get(
                item.model_name,
                0,
            )
            + 1
        )

    completed_count = len(
        completed_runs
    )

    recent_runs = [
        AIAnalysisRunSummaryItem(
            analysis_run_id=(
                item.analysis_run_id
            ),
            started_at=(
                item.started_at
            ),
            team_name=(
                item.team_name
            ),
            model_name=(
                item.model_name
            ),
            status=item.status,
            verification_status=(
                item.verification_status
            ),
            revised=(
                item.revised
            ),
            review_attempt_count=(
                item.review_attempt_count
            ),
            total_tokens=(
                item.total_tokens
            ),
            latency_ms=(
                item.latency_ms
            ),
            error_type=(
                item.error_type
            ),
        )
        for item in records[
            :10
        ]
    ]

    return AIOperationsSummary(
        window_days=window_days,
        total_runs=total_runs,
        approved_runs=approved_runs,
        verification_failed_runs=(
            verification_failed_runs
        ),
        provider_failed_runs=(
            provider_failed_runs
        ),
        failed_runs=failed_runs,
        in_progress_runs=(
            in_progress_runs
        ),
        revised_runs=revised_runs,
        approval_rate_pct=(
            _percentage(
                approved_runs,
                completed_count,
            )
        ),
        revision_rate_pct=(
            _percentage(
                revised_runs,
                completed_count,
            )
        ),
        verification_failure_rate_pct=(
            _percentage(
                verification_failed_runs,
                completed_count,
            )
        ),
        average_latency_ms=(
            average_latency_ms
        ),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=(
            estimated_cost_usd
        ),
        model_counts=(
            model_counts
        ),
        recent_runs=(
            recent_runs
        ),
    )