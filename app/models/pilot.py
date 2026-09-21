from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


PilotAnswer = Literal[
    "yes",
    "maybe",
    "no",
]


class PilotInterestCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    coach_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        min_length=5,
        max_length=254,
    )

    club_or_team: str = Field(
        min_length=2,
        max_length=150,
    )

    role: str = Field(
        min_length=2,
        max_length=100,
    )

    would_use_in_real_matches: PilotAnswer

    join_private_pilot: PilotAnswer

    willingness_to_pay_monthly_gbp: (
        int | None
    ) = Field(
        default=None,
        ge=0,
        le=10000,
    )

    most_valuable_feature: str | None = Field(
        default=None,
        max_length=1000,
    )

    feedback: str | None = Field(
        default=None,
        max_length=3000,
    )


class PilotInterestResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    pilot_interest_id: UUID

    created_at: datetime

    coach_name: str

    email: str

    club_or_team: str

    role: str

    would_use_in_real_matches: PilotAnswer

    join_private_pilot: PilotAnswer

    willingness_to_pay_monthly_gbp: (
        int | None
    )

    most_valuable_feature: str | None

    feedback: str | None

    status: Literal[
        "recorded"
    ] = "recorded"