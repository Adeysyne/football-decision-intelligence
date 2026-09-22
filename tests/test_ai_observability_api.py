import importlib

from fastapi.testclient import (
    TestClient,
)
from sqlalchemy import select

from app.db.models import (
    AIAnalysisRunRecord,
)
from app.main import app
from app.services.ai_reasoning import (
    AIAnalysisError,
)
from tests.conftest import (
    TestingSessionLocal,
)
from tests.test_decision_engine import (
    BASE_SCENARIO,
)


client = TestClient(
    app
)


api_module = importlib.import_module(
    "app.api.ai_analysis"
)


def _approved_result():
    return {
        "decision_brief": {
            "test": True
        },
        "tactical_knowledge": {
            "items": []
        },
        "ai_reasoning": {
            "summary": (
                "Verified test reasoning."
            )
        },
        "verification": {
            "status": "approved",
            "revised": True,
            "review_attempts": [
                {
                    "status": (
                        "needs_revision"
                    )
                },
                {
                    "status": (
                        "approved"
                    )
                },
            ],
        },
        "models": {
            "reasoning": (
                "gpt-5.6-luna"
            ),
            "first_review": (
                "gpt-5.6-luna"
            ),
            "revision": (
                "gpt-5.6-luna"
            ),
            "second_review": (
                "gpt-5.6-luna"
            ),
        },
        "usage": {
            "reasoning": {
                "input_tokens": 100,
                "output_tokens": 40,
                "total_tokens": 140,
            },
            "first_review": {
                "input_tokens": 80,
                "output_tokens": 20,
                "total_tokens": 100,
            },
            "revision": {
                "input_tokens": 90,
                "output_tokens": 30,
                "total_tokens": 120,
            },
            "second_review": {
                "input_tokens": 70,
                "output_tokens": 15,
                "total_tokens": 85,
            },
        },
    }


def test_verified_analysis_records_usage(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module,
        "analyse_with_verification",
        lambda scenario: (
            _approved_result()
        ),
    )

    response = client.post(
        "/api/v1/ai/analyse-verified",
        json=BASE_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    assert body[
        "analysis_run_id"
    ]

    with TestingSessionLocal() as db:
        record = db.get(
            AIAnalysisRunRecord,
            body[
                "analysis_run_id"
            ],
        )

        assert record is not None

        assert (
            record.status
            == "approved"
        )

        assert (
            record.verification_status
            == "approved"
        )

        assert (
            record.revised
            is True
        )

        assert (
            record.review_attempt_count
            == 2
        )

        assert (
            record.input_tokens
            == 340
        )

        assert (
            record.output_tokens
            == 105
        )

        assert (
            record.total_tokens
            == 445
        )

        assert (
            record.latency_ms
            is not None
        )


def test_verification_failure_is_logged(
    monkeypatch,
):
    def fail(
        scenario,
    ):
        raise AIAnalysisError(
            "AI reasoning could not be "
            "verified after one "
            "controlled revision.",
            502,
        )

    monkeypatch.setattr(
        api_module,
        "analyse_with_verification",
        fail,
    )

    response = client.post(
        "/api/v1/ai/analyse-verified",
        json=BASE_SCENARIO,
    )

    assert response.status_code == 502

    with TestingSessionLocal() as db:
        record = db.scalar(
            select(
                AIAnalysisRunRecord
            )
        )

        assert record is not None

        assert (
            record.status
            == "verification_failed"
        )

        assert (
            record.revised
            is True
        )

        assert (
            record.review_attempt_count
            == 2
        )

        assert (
            record.error_type
            == "VerificationFailure"
        )


def test_provider_failure_is_logged(
    monkeypatch,
):
    def fail(
        scenario,
    ):
        raise AIAnalysisError(
            "AI provider unavailable. "
            "Try again later.",
            503,
        )

    monkeypatch.setattr(
        api_module,
        "analyse_with_verification",
        fail,
    )

    response = client.post(
        "/api/v1/ai/analyse-verified",
        json=BASE_SCENARIO,
    )

    assert response.status_code == 503

    with TestingSessionLocal() as db:
        record = db.scalar(
            select(
                AIAnalysisRunRecord
            )
        )

        assert record is not None

        assert (
            record.status
            == "provider_failed"
        )

        assert (
            record.error_type
            == "ProviderFailure"
        )


def test_observability_failure_does_not_break_analysis(
    monkeypatch,
):
    monkeypatch.setattr(
        api_module,
        "start_ai_analysis_run",
        lambda **kwargs: (
            (_ for _ in ()).throw(
                RuntimeError(
                    "Telemetry unavailable"
                )
            )
        ),
    )

    monkeypatch.setattr(
        api_module,
        "analyse_with_verification",
        lambda scenario: (
            _approved_result()
        ),
    )

    response = client.post(
        "/api/v1/ai/analyse-verified",
        json=BASE_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body[
            "verification"
        ]["status"]
        == "approved"
    )

    assert (
        "analysis_run_id"
        not in body
    )


def test_usage_summary_ignores_unused_stages():
    result = (
        api_module.summarize_usage(
            {
                "reasoning": {
                    "input_tokens": 100,
                    "output_tokens": 20,
                    "total_tokens": 120,
                },
                "first_review": {
                    "input_tokens": 70,
                    "output_tokens": 10,
                    "total_tokens": 80,
                },
                "revision": None,
                "second_review": None,
            }
        )
    )

    assert (
        result[
            "input_tokens"
        ]
        == 170
    )

    assert (
        result[
            "output_tokens"
        ]
        == 30
    )

    assert (
        result[
            "total_tokens"
        ]
        == 200
    )