from pydantic import BaseModel, ConfigDict, Field


class OptionExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_id: str
    explanation: str = Field(min_length=1)
    main_risk: str = Field(min_length=1)
    assumption_to_check: str = Field(min_length=1)


class AIReasoning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    option_explanations: list[OptionExplanation] = Field(
        min_length=1
    )
    missing_information: list[str]
    questions_for_coach: list[str]