from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TeamProfileCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    team_name: str = Field(
        min_length=2,
        max_length=100,
    )

    default_formation: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
    )

    tactical_identity: str | None = Field(
        default=None,
        max_length=1500,
    )

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class TeamProfileResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    team_id: UUID
    team_name: str

    created_at: datetime
    updated_at: datetime

    default_formation: str | None
    tactical_identity: str | None
    notes: str | None


class TeamHistorySummary(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    team_id: UUID
    team_name: str

    scenario_count: int
    decision_count: int
    selection_count: int
    outcome_count: int

    engine_leader_selected_count: int

    assessment_counts: dict[str, int]

    scenario_profile_counts: dict[str, int]

    data_note: str = (
        "Historical counts are descriptive only. "
        "Coach assessments do not prove that a tactical "
        "decision caused the recorded match outcome."
    )


class LatestCoachSelection(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    selection_id: UUID
    decision_id: UUID

    selected_option_id: str
    selected_at: datetime

    rationale: str | None


class LatestDecisionOutcome(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    outcome_id: UUID
    decision_id: UUID

    recorded_at: datetime

    final_our_score: int
    final_opponent_score: int

    coach_assessment: str

    outcome_summary: str

    observed_effects: list[str]

    next_time_notes: str | None


class TeamLatestWorkflow(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    team_id: UUID
    team_name: str

    scenario_id: UUID
    scenario_created_at: datetime

    scenario: dict[str, Any]

    decision_id: UUID | None = None
    decision_created_at: datetime | None = None

    decision_brief: (
        dict[str, Any] | None
    ) = None

    selection: (
        LatestCoachSelection | None
    ) = None

    outcome: (
        LatestDecisionOutcome | None
    ) = None

    is_complete: bool