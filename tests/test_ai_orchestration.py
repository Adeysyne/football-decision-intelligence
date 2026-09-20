from copy import deepcopy

import pytest

from app.models.ai_reasoning import AIReasoning
from app.models.ai_review import AIReview
from app.models.scenario import ScenarioCreate
from app.services import ai_orchestration as service
from app.services.ai_reasoning import AIAnalysisError
from app.services.ai_reasoning import prepare_reasoning_input
from tests.test_decision_engine import BASE_SCENARIO


def _scenario() -> ScenarioCreate:
    return ScenarioCreate(
        **BASE_SCENARIO
    )


def _draft_result() -> dict:
    scenario = _scenario()

    payload = prepare_reasoning_input(
        scenario
    )

    reasoning = AIReasoning(
        summary=(
            "Compare the supplied tactical options."
        ),
        option_explanations=[
            {
                "option_id": option[
                    "option_id"
                ],
                "explanation": (
                    "Consider the supplied tactical "
                    "trade-offs."
                ),
                "main_risk": (
                    "The original problem may remain."
                ),
                "assumption_to_check": (
                    "Suitable cover is available."
                ),
            }
            for option
            in payload[
                "decision_brief"
            ]["options"]
        ],
        missing_information=[
            "Current player fitness."
        ],
        questions_for_coach=[
            "Is the replacement ready?"
        ],
    )

    return {
        "decision_brief": deepcopy(
            payload[
                "decision_brief"
            ]
        ),
        "tactical_knowledge": deepcopy(
            payload[
                "tactical_knowledge"
            ]
        ),
        "ai_reasoning": reasoning.model_dump(
            mode="json"
        ),
        "model": "reasoning-model",
        "usage": None,
    }


def _approved_review() -> dict:
    return {
        "review": AIReview(
            status="approved",
            summary=(
                "No material issues found."
            ),
            issues=[],
        ).model_dump(
            mode="json"
        ),
        "model": "review-model",
        "usage": None,
    }


def _revision_review() -> dict:
    return {
        "review": AIReview(
            status="needs_revision",
            summary=(
                "One unsupported observation."
            ),
            issues=[
                {
                    "claim_path": "summary",
                    "quote": "Compare",
                    "problem": (
                        "The wording should be "
                        "more cautious."
                    ),
                    "suggested_revision": (
                        "Review the supplied "
                        "tactical options."
                    ),
                }
            ],
        ).model_dump(
            mode="json"
        ),
        "model": "review-model",
        "usage": None,
    }


def test_approved_draft_returns_without_revision(
    monkeypatch,
):
    draft_result = _draft_result()

    monkeypatch.setattr(
        service,
        "analyse_with_ai",
        lambda scenario: deepcopy(
            draft_result
        ),
    )

    monkeypatch.setattr(
        service,
        "review_ai_reasoning",
        lambda payload, draft: (
            _approved_review()
        ),
    )

    revision_called = False

    def fake_revision(*args, **kwargs):
        nonlocal revision_called
        revision_called = True

        return {}

    monkeypatch.setattr(
        service,
        "revise_ai_reasoning",
        fake_revision,
    )

    result = service.analyse_with_verification(
        _scenario()
    )

    assert (
        result["verification"]["status"]
        == "approved"
    )

    assert (
        result["verification"]["revised"]
        is False
    )

    assert (
        len(
            result[
                "verification"
            ]["review_attempts"]
        )
        == 1
    )

    assert revision_called is False


def test_failed_first_review_triggers_one_revision(
    monkeypatch,
):
    draft_result = _draft_result()

    monkeypatch.setattr(
        service,
        "analyse_with_ai",
        lambda scenario: deepcopy(
            draft_result
        ),
    )

    reviews = [
        _revision_review(),
        _approved_review(),
    ]

    def fake_review(
        payload,
        draft,
    ):
        return reviews.pop(0)

    monkeypatch.setattr(
        service,
        "review_ai_reasoning",
        fake_review,
    )

    revised = deepcopy(
        draft_result[
            "ai_reasoning"
        ]
    )

    revised["summary"] = (
        "Review the supplied tactical options."
    )

    monkeypatch.setattr(
        service,
        "revise_ai_reasoning",
        lambda **kwargs: {
            "ai_reasoning": revised,
            "model": "revision-model",
            "usage": None,
        },
    )

    result = service.analyse_with_verification(
        _scenario()
    )

    assert (
        result["verification"]["status"]
        == "approved"
    )

    assert (
        result["verification"]["revised"]
        is True
    )

    assert (
        len(
            result[
                "verification"
            ]["review_attempts"]
        )
        == 2
    )

    assert (
        result["ai_reasoning"]["summary"]
        == revised["summary"]
    )


def test_second_failed_review_rejects_output(
    monkeypatch,
):
    draft_result = _draft_result()

    monkeypatch.setattr(
        service,
        "analyse_with_ai",
        lambda scenario: deepcopy(
            draft_result
        ),
    )

    monkeypatch.setattr(
        service,
        "review_ai_reasoning",
        lambda payload, draft: (
            _revision_review()
        ),
    )

    monkeypatch.setattr(
        service,
        "revise_ai_reasoning",
        lambda **kwargs: {
            "ai_reasoning": deepcopy(
                draft_result[
                    "ai_reasoning"
                ]
            ),
            "model": "revision-model",
            "usage": None,
        },
    )

    with pytest.raises(
        AIAnalysisError
    ) as caught:
        service.analyse_with_verification(
            _scenario()
        )

    assert (
        caught.value.status_code
        == 502
    )

    assert (
        "could not be verified"
        in str(caught.value).lower()
    )


def test_original_engine_output_is_preserved(
    monkeypatch,
):
    draft_result = _draft_result()

    original_brief = deepcopy(
        draft_result[
            "decision_brief"
        ]
    )

    original_knowledge = deepcopy(
        draft_result[
            "tactical_knowledge"
        ]
    )

    monkeypatch.setattr(
        service,
        "analyse_with_ai",
        lambda scenario: deepcopy(
            draft_result
        ),
    )

    monkeypatch.setattr(
        service,
        "review_ai_reasoning",
        lambda payload, draft: (
            _approved_review()
        ),
    )

    result = service.analyse_with_verification(
        _scenario()
    )

    assert (
        result["decision_brief"]
        == original_brief
    )

    assert (
        result["tactical_knowledge"]
        == original_knowledge
    )