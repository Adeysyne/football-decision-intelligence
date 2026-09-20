from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from openai import OpenAIError

from app.main import app
from app.models.ai_reasoning import AIReasoning
from app.models.scenario import ScenarioCreate
from app.services import ai_reasoning as service
from tests.test_decision_engine import BASE_SCENARIO


client = TestClient(app)
ENDPOINT = "/api/v1/ai/analyse"


@pytest.fixture
def fake_ai(monkeypatch):
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(
            openai_api_key="test-key",
            openai_model="gpt-5.6-luna",
        ),
    )

    provider = MagicMock()
    provider.__enter__.return_value = provider

    monkeypatch.setattr(
        service,
        "OpenAI",
        MagicMock(return_value=provider),
    )

    scenario = ScenarioCreate(**BASE_SCENARIO)
    brief = service.prepare_reasoning_input(
        scenario
    )["decision_brief"]

    reasoning = AIReasoning(
        summary="Compare the supplied tactical options.",
        option_explanations=[
            {
                "option_id": option["option_id"],
                "explanation": "Consider the stated trade-offs.",
                "main_risk": "The original problem may remain.",
                "assumption_to_check": "Suitable cover is available.",
            }
            for option in brief["options"]
        ],
        missing_information=["Current player fitness."],
        questions_for_coach=["Is the replacement ready?"],
    )

    provider.responses.parse.return_value = SimpleNamespace(
        status="completed",
        output_parsed=reasoning,
        model="gpt-5.6-luna",
        usage=None,
    )

    return provider.responses.parse


def test_ai_endpoint_preserves_engine_brief(fake_ai):
    response = client.post(
        ENDPOINT,
        json=BASE_SCENARIO,
    )

    assert response.status_code == 200

    expected = service.prepare_reasoning_input(
        ScenarioCreate(**BASE_SCENARIO)
    )["decision_brief"]

    assert response.json()["decision_brief"] == expected
    assert response.json()["ai_reasoning"]["summary"]
    fake_ai.assert_called_once()


@pytest.mark.parametrize(
    "failure",
    [
        "missing",
        "duplicate",
        "unknown",
        "refusal",
        "incomplete",
        "percentage",
    ],
)
def test_invalid_ai_output_is_rejected(fake_ai, failure):
    result = fake_ai.return_value
    explanations = result.output_parsed.option_explanations

    if failure == "missing":
        explanations.pop()

    elif failure == "duplicate":
        explanations[-1].option_id = explanations[0].option_id

    elif failure == "unknown":
        explanations[-1].option_id = "unknown_option"

    elif failure == "refusal":
        result.output_parsed = None

    elif failure == "incomplete":
        result.status = "incomplete"

    elif failure == "percentage":
        result.output_parsed.summary = "This has 80% success."

    response = client.post(
        ENDPOINT,
        json=BASE_SCENARIO,
    )

    assert response.status_code == 502
    assert "ai_reasoning" not in response.json()


def test_provider_error_does_not_expose_details(fake_ai):
    fake_ai.side_effect = OpenAIError(
        "private-provider-detail"
    )

    response = client.post(
        ENDPOINT,
        json=BASE_SCENARIO,
    )

    assert response.status_code == 503
    assert "private-provider-detail" not in response.text


def test_missing_key_prevents_api_call(fake_ai, monkeypatch):
    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key=""),
    )

    response = client.post(
        ENDPOINT,
        json=BASE_SCENARIO,
    )

    assert response.status_code == 503
    fake_ai.assert_not_called()