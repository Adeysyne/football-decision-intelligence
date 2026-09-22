from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


AnalysisStatus = Literal[
    "started",
    "approved",
    "verification_failed",
    "provider_failed",
    "failed",
]


class AIAnalysisRunResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    analysis_run_id: UUID

    started_at: datetime
    completed_at: datetime | None

    team_name: str
    model_name: str

    status: AnalysisStatus

    latency_ms: int | None

    verification_status: (
        str | None
    )

    revised: bool

    review_attempt_count: int

    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None

    estimated_cost_usd: (
        float | None
    )

    error_type: str | None

    error_message: str | None


class AIAnalysisRunSummaryItem(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid"
    )

    analysis_run_id: UUID

    started_at: datetime

    team_name: str

    model_name: str

    status: AnalysisStatus

    verification_status: (
        str | None
    )

    revised: bool

    review_attempt_count: int

    total_tokens: int | None

    latency_ms: int | None

    error_type: str | None


class AIOperationsSummary(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid"
    )

    window_days: int

    total_runs: int

    approved_runs: int

    verification_failed_runs: int

    provider_failed_runs: int

    failed_runs: int

    in_progress_runs: int

    revised_runs: int

    approval_rate_pct: float

    revision_rate_pct: float

    verification_failure_rate_pct: (
        float
    )

    average_latency_ms: (
        float | None
    )

    input_tokens: int

    output_tokens: int

    total_tokens: int

    estimated_cost_usd: float

    model_counts: dict[str, int]

    recent_runs: list[
        AIAnalysisRunSummaryItem
    ]