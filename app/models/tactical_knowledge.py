from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.decision import ScenarioProfile


KnowledgeEvidenceType = Literal[
    "internal_tactical_principle",
]


class TacticalKnowledgeItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    knowledge_id: str = Field(
        min_length=1,
    )

    title: str = Field(
        min_length=1,
    )

    principle: str = Field(
        min_length=1,
    )

    caveat: str = Field(
        min_length=1,
    )

    tags: list[str] = Field(
        min_length=1,
    )

    evidence_type: KnowledgeEvidenceType = (
        "internal_tactical_principle"
    )


class RetrievedTacticalKnowledge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_profile: ScenarioProfile

    context_tags: list[str]

    items: list[TacticalKnowledgeItem]

    note: str = (
        "These are transparent internal tactical principles. "
        "They are not probabilities, external research citations, "
        "tracking data, or claims about either team."
    )