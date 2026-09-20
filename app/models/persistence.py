from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.models.decision import DecisionBrief


class PersistedDecisionResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    decision_id: UUID
    scenario_id: UUID
    created_at: datetime
    decision_brief: DecisionBrief


class CoachSelectionCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    selected_option_id: str = Field(
        min_length=1,
        max_length=50,
    )

    rationale: str | None = Field(
        default=None,
        max_length=1500,
    )


class CoachSelectionResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    selection_id: UUID
    decision_id: UUID
    selected_option_id: str
    selected_at: datetime
    rationale: str | None


class DecisionOutcomeCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    final_our_score: int = Field(
        ge=0,
        le=30,
    )

    final_opponent_score: int = Field(
        ge=0,
        le=30,
    )

    coach_assessment: Literal[
        "helped",
        "neutral",
        "hurt",
        "unclear",
    ]

    outcome_summary: str = Field(
        min_length=5,
        max_length=2000,
    )

    observed_effects: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    next_time_notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class DecisionOutcomeResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    outcome_id: UUID
    decision_id: UUID
    recorded_at: datetime

    final_our_score: int
    final_opponent_score: int

    coach_assessment: Literal[
        "helped",
        "neutral",
        "hurt",
        "unclear",
    ]

    outcome_summary: str
    observed_effects: list[str]
    next_time_notes: str | None


class DecisionFeedbackResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    decision_id: UUID

    selection: (
        CoachSelectionResponse
        | None
    )

    outcome: (
        DecisionOutcomeResponse
        | None
    )