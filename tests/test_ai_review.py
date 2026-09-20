from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from openai import OpenAIError
from pydantic import ValidationError

from app.models.ai_reasoning import AIReasoning
from app.models.ai_review import AIReview
from app.models.scenario import ScenarioCreate
from app.services import ai_review as service
from app.services.ai_reasoning import (
    AIAnalysisError,
    prepare_reasoning_input,
)
from tests.test_decision_engine import BASE_SCENARIO


ISSUE = {
    "claim_path": "summary",
    "quote": "further 2v1 situations",
    "problem": "Previous 2v1 situations were not reported.",
    "suggested_revision": "Potential 2v1 situations.",
}


@pytest.fixture
def setup_review(monkeypatch):
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

    payload = prepare_reasoning_input(
        ScenarioCreate(**BASE_SCENARIO)
    )

    draft = AIReasoning(
        summary="Reduce exposure to further 2v1 situations.",
        option_explanations=[
            {
                "option_id": option["option_id"],
                "explanation": "Consider the supplied trade-offs.",
                "main_risk": "The original problem may remain.",
                "assumption_to_check": "Suitable cover is available.",
            }
            for option in payload["decision_brief"]["options"]
        ],
        missing_information=[],
        questions_for_coach=[],
    )

    provider.responses.parse.return_value = SimpleNamespace(
        status="completed",
        output_parsed=AIReview(
            status="needs_revision",
            summary="One unsupported observation.",
            issues=[ISSUE],
        ),
        model="gpt-5.6-luna",
        usage=None,
    )

    return provider.responses.parse, payload, draft


def test_review_preserves_original_input(setup_review):
    fake, payload, draft = setup_review
    original_payload = deepcopy(payload)
    original_draft = draft.model_dump()

    result = service.review_ai_reasoning(payload, draft)

    assert result["review"]["status"] == "needs_revision"
    assert payload == original_payload
    assert draft.model_dump() == original_draft
    fake.assert_called_once()


def test_approved_review_is_returned(setup_review):
    fake, payload, draft = setup_review
    draft.summary = "Compare the supplied tactical options."

    fake.return_value.output_parsed = AIReview(
        status="approved",
        summary="No material issues found.",
        issues=[],
    )

    result = service.review_ai_reasoning(payload, draft)

    assert result["review"]["status"] == "approved"
    assert result["review"]["issues"] == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("claim_path", "unknown.field"),
        ("quote", "The goalkeeper is injured."),
    ],
)
def test_invented_review_citation_is_rejected(
    setup_review, field, value
):
    fake, payload, draft = setup_review
    report = fake.return_value.output_parsed.model_dump()
    report["issues"][0][field] = value
    fake.return_value.output_parsed = AIReview(**report)

    with pytest.raises(AIAnalysisError) as caught:
        service.review_ai_reasoning(payload, draft)

    assert caught.value.status_code == 502


def test_approval_cannot_contain_unresolved_issues():
    with pytest.raises(ValidationError):
        AIReview(
            status="approved",
            summary="Conflicting review.",
            issues=[ISSUE],
        )


def test_provider_error_is_sanitised(setup_review):
    fake, payload, draft = setup_review
    fake.side_effect = OpenAIError("private-provider-detail")

    with pytest.raises(AIAnalysisError) as caught:
        service.review_ai_reasoning(payload, draft)

    assert caught.value.status_code == 503
    assert "private-provider-detail" not in str(caught.value)


@pytest.mark.parametrize("failure", ["refusal", "incomplete"])
def test_unfinished_review_is_rejected(setup_review, failure):
    fake, payload, draft = setup_review

    if failure == "refusal":
        fake.return_value.output_parsed = None
    else:
        fake.return_value.status = "incomplete"

    with pytest.raises(AIAnalysisError) as caught:
        service.review_ai_reasoning(payload, draft)

    assert caught.value.status_code == 502


def test_missing_key_prevents_review_call(
    setup_review, monkeypatch
):
    fake, payload, draft = setup_review

    monkeypatch.setattr(
        service,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key=""),
    )

    with pytest.raises(AIAnalysisError) as caught:
        service.review_ai_reasoning(payload, draft)

    assert caught.value.status_code == 503
    fake.assert_not_called()