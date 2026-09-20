from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.decision import DecisionBrief


class PersistedDecisionResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    decision_id: UUID
    scenario_id: UUID
    created_at: datetime
    decision_brief: DecisionBrief