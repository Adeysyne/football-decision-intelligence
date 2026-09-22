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