import importlib
from datetime import (
    datetime,
    timezone,
)

from fastapi.testclient import (
    TestClient,
)

from app.db.models import (
    AIAnalysisRunRecord,
)
from app.main import app
from tests.conftest import (
    TestingSessionLocal,
)


client = TestClient(
    app
)


operations_module = (
    importlib.import_module(
        "app.api.operations"
    )
)


def _enable_admin(
    monkeypatch,
):
    settings = (
        operations_module.get_settings()
    )

    monkeypatch.setattr(
        settings,
        "admin_access_code",
        "test-admin-code",
    )


def _headers():
    return {
        "X-Admin-Access-Code": (
            "test-admin-code"
        )
    }


def _record(
    *,
    status: str,
    revised: bool = False,
    latency_ms: int | None = 1000,
    input_tokens: int | None = 100,
    output_tokens: int | None = 50,
    total_tokens: int | None = 150,
    error_type: str | None = None,
):
    return AIAnalysisRunRecord(
        started_at=datetime.now(
            timezone.utc
        ),
        completed_at=datetime.now(
            timezone.utc
        ),
        team_name="Ops Test FC",
        model_name="gpt-5.6-luna",
        status=status,
        latency_ms=latency_ms,
        verification_status=(
            "approved"
            if status
            == "approved"
            else (
                "needs_revision"
                if status
                == "verification_failed"
                else None
            )
        ),
        revised=revised,
        review_attempt_count=(
            2
            if revised
            else 1
        ),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=None,
        error_type=error_type,
        error_message=None,
    )


def test_operations_requires_admin_code(
    monkeypatch,
):
    _enable_admin(
        monkeypatch
    )

    response = client.get(
        "/api/v1/operations/ai-summary"
    )

    assert response.status_code == 401


def test_operations_rejects_wrong_code(
    monkeypatch,
):
    _enable_admin(
        monkeypatch
    )

    response = client.get(
        "/api/v1/operations/ai-summary",
        headers={
            "X-Admin-Access-Code": (
                "wrong-code"
            )
        },
    )

    assert response.status_code == 401


def test_operations_rejects_invalid_window(
    monkeypatch,
):
    _enable_admin(
        monkeypatch
    )

    response = client.get(
        (
            "/api/v1/operations/"
            "ai-summary?window_days=0"
        ),
        headers=_headers(),
    )

    assert response.status_code == 422


def test_empty_operations_summary(
    monkeypatch,
):
    _enable_admin(
        monkeypatch
    )

    response = client.get(
        "/api/v1/operations/ai-summary",
        headers=_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body[
        "total_runs"
    ] == 0

    assert body[
        "approval_rate_pct"
    ] == 0.0

    assert body[
        "total_tokens"
    ] == 0


def test_operations_summary_aggregates_runs(
    monkeypatch,
):
    _enable_admin(
        monkeypatch
    )

    with TestingSessionLocal() as db:
        db.add_all(
            [
                _record(
                    status="approved",
                    revised=False,
                    latency_ms=1000,
                    input_tokens=100,
                    output_tokens=50,
                    total_tokens=150,
                ),
                _record(
                    status="approved",
                    revised=True,
                    latency_ms=3000,
                    input_tokens=200,
                    output_tokens=100,
                    total_tokens=300,
                ),
                _record(
                    status=(
                        "verification_failed"
                    ),
                    revised=True,
                    latency_ms=2000,
                    input_tokens=None,
                    output_tokens=None,
                    total_tokens=None,
                    error_type=(
                        "VerificationFailure"
                    ),
                ),
            ]
        )

        db.commit()

    response = client.get(
        "/api/v1/operations/ai-summary",
        headers=_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert body[
        "total_runs"
    ] == 3

    assert body[
        "approved_runs"
    ] == 2

    assert body[
        "verification_failed_runs"
    ] == 1

    assert body[
        "revised_runs"
    ] == 2

    assert body[
        "approval_rate_pct"
    ] == 66.67

    assert body[
        "revision_rate_pct"
    ] == 66.67

    assert body[
        "verification_failure_rate_pct"
    ] == 33.33

    assert body[
        "average_latency_ms"
    ] == 2000.0

    assert body[
        "input_tokens"
    ] == 300

    assert body[
        "output_tokens"
    ] == 150

    assert body[
        "total_tokens"
    ] == 450


def test_operations_returns_recent_runs(
    monkeypatch,
):
    _enable_admin(
        monkeypatch
    )

    with TestingSessionLocal() as db:
        db.add(
            _record(
                status="approved"
            )
        )

        db.commit()

    response = client.get(
        "/api/v1/operations/ai-summary",
        headers=_headers(),
    )

    assert response.status_code == 200

    body = response.json()

    assert len(
        body[
            "recent_runs"
        ]
    ) == 1

    recent = body[
        "recent_runs"
    ][0]

    assert (
        recent[
            "team_name"
        ]
        == "Ops Test FC"
    )

    assert (
        recent[
            "status"
        ]
        == "approved"
    )