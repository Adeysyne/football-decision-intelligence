from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TacticalOptionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(
        min_length=1,
        max_length=80,
        examples=["Switch to 5-4-1"],
    )
    description: str = Field(
        min_length=5,
        max_length=500,
        examples=[
            "Introduce an extra centre-back and defend with a five-player back line."
        ],
    )


class ScenarioCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    team_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Sheffield FC"],
    )

    opponent_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["Example United"],
    )

    minute: int = Field(
        ge=0,
        le=130,
        examples=[68],
    )

    our_score: int = Field(
        ge=0,
        le=30,
        examples=[1],
    )

    opponent_score: int = Field(
        ge=0,
        le=30,
        examples=[0],
    )

    our_formation: str = Field(
        min_length=3,
        max_length=20,
        examples=["4-2-3-1"],
    )

    opponent_formation: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
        examples=["4-3-3"],
    )

    yellow_cards: list[str] = Field(
        default_factory=list,
        max_length=11,
        examples=[["Left-back"]],
    )

    red_cards: list[str] = Field(
        default_factory=list,
        max_length=11,
    )

    available_substitutions: list[str] = Field(
        default_factory=list,
        max_length=15,
        examples=[
            [
                "Defensive midfielder",
                "Centre-back",
                "Left-back",
            ]
        ],
    )

    tactical_problem: str = Field(
        min_length=10,
        max_length=1500,
        examples=[
            "Their right winger is repeatedly getting behind our left-back."
        ],
    )

    objective: str = Field(
        min_length=5,
        max_length=500,
        examples=[
            "Protect the lead without completely losing our attacking threat."
        ],
    )

    coach_observations: str | None = Field(
        default=None,
        max_length=2000,
        examples=[
            "Our left-back is already booked and the opposition right-back is beginning to overlap."
        ],
    )

    options: list[TacticalOptionInput] = Field(
        default_factory=list,
        max_length=5,
    )

    requested_option_count: int = Field(
        default=3,
        ge=2,
        le=4,
        description=(
            "Number of tactical alternatives the decision engine should "
            "generate when the coach has not supplied options."
        ),
    )


class ScenarioResponse(BaseModel):
    scenario_id: UUID

    status: Literal["validated"] = "validated"

    created_at: datetime

    scenario: ScenarioCreate

    next_step: Literal["decision_engine"] = "decision_engine"