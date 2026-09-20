from typing import Literal

from pydantic import BaseModel, Field


OptionCategory = Literal[
    "instruction",
    "personnel",
    "structural",
]


ScenarioProfile = Literal[
    "protect_lead",
    "chase_game",
    "control_game",
    "balanced",
]


class DecisionScores(BaseModel):
    """
    All scores use a 1-5 scale.

    1 = weak alignment / poor outcome for that dimension
    3 = neutral / moderate
    5 = strong alignment / favourable outcome

    These scores are transparent decision-support signals,
    not probabilities.
    """

    defensive_stability: int = Field(ge=1, le=5)
    attacking_threat: int = Field(ge=1, le=5)
    wide_area_control: int = Field(ge=1, le=5)
    midfield_control: int = Field(ge=1, le=5)
    transition_security: int = Field(ge=1, le=5)
    personnel_fit: int = Field(ge=1, le=5)
    tactical_continuity: int = Field(ge=1, le=5)
    objective_alignment: int = Field(ge=1, le=5)


class TacticalOptionAnalysis(BaseModel):
    option_id: str

    label: str

    description: str

    category: OptionCategory

    scores: DecisionScores

    total_score: int = Field(
        ge=8,
        le=40,
        description=(
            "Unweighted diagnostic total across all eight dimensions."
        ),
    )

    weighted_score: float = Field(
        ge=1.0,
        le=5.0,
        description=(
            "Objective-aware weighted average on a 1-5 scale."
        ),
    )

    strengths: list[str]

    risks: list[str]

    assumptions: list[str]


class DecisionBrief(BaseModel):
    scenario_summary: str

    scenario_profile: ScenarioProfile

    generated_from: Literal[
        "engine_options",
        "coach_options",
    ]

    score_weights: dict[str, float]

    options: list[TacticalOptionAnalysis]

    leading_option_id: str

    leading_option_reason: str

    main_tradeoff: str

    monitor_next: list[str]

    confidence: Literal[
        "low",
        "medium",
    ]

    scoring_note: str

    coach_decision_required: bool = True