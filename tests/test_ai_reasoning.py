import json

import pytest
from pydantic import ValidationError

from app.models.ai_reasoning import AIReasoning
from app.models.scenario import ScenarioCreate
from app.services.ai_reasoning import serialize_reasoning_input
from app.services.decision_engine import build_decision_brief
from tests.test_decision_engine import BASE_SCENARIO


def test_ai_input_preserves_engine_output():
    scenario = ScenarioCreate(**BASE_SCENARIO)
    expected = build_decision_brief(scenario).model_dump(
        mode="json"
    )

    payload = json.loads(serialize_reasoning_input(scenario))

    assert payload["decision_brief"] == expected
    assert payload["scenario"] == scenario.model_dump(mode="json")


def test_api_key_is_not_in_ai_input(monkeypatch):
    sentinel = "test-secret-must-not-appear"
    monkeypatch.setenv("OPENAI_API_KEY", sentinel)
    scenario = ScenarioCreate(**BASE_SCENARIO)

    assert sentinel not in serialize_reasoning_input(scenario)


def test_ai_schema_rejects_extra_score_fields():
    with pytest.raises(ValidationError):
        AIReasoning(
            summary="Compare the supplied tactical options.",
            option_explanations=[{
                "option_id": "option_1",
                "explanation": "Preserves the current shape.",
                "main_risk": "The original mismatch may remain.",
                "assumption_to_check": "Cover is available.",
            }],
            missing_information=[],
            questions_for_coach=[],
            replacement_score=5,
        )