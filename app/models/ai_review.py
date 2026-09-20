from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReviewIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_path: str = Field(min_length=1)
    quote: str = Field(min_length=1)
    problem: str = Field(min_length=1)
    suggested_revision: str = Field(min_length=1)


class AIReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["approved", "needs_revision"]
    summary: str = Field(min_length=1)
    issues: list[ReviewIssue]

    @model_validator(mode="after")
    def check_status(self) -> "AIReview":
        if (self.status == "needs_revision") != bool(self.issues):
            raise ValueError(
                "Review status must agree with its issues."
            )
        return self