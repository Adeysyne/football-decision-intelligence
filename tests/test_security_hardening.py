from fastapi.testclient import (
    TestClient,
)

import app.main as main_module
from app.core.security import (
    InMemoryRateLimiter,
    security_limiter,
)
from app.main import app


client = TestClient(
    app
)


def setup_function():
    security_limiter.clear()


def teardown_function():
    security_limiter.clear()


def test_security_headers_are_present():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "X-Content-Type-Options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "X-Frame-Options"
        ]
        == "DENY"
    )

    assert (
        response.headers[
            "Referrer-Policy"
        ]
        == "no-referrer"
    )

    assert (
        response.headers[
            "Cache-Control"
        ]
        == "no-store"
    )


def test_oversized_payload_is_rejected(
    monkeypatch,
):
    monkeypatch.setattr(
        main_module.settings,
        "max_request_bytes",
        100,
    )

    response = client.post(
        "/",
        content=(
            b"x"
            * 101
        ),
    )

    assert response.status_code == 413

    assert (
        response.headers.get(
            "X-Request-ID"
        )
        is not None
    )


def test_rate_limiter_blocks_after_limit():
    limiter = (
        InMemoryRateLimiter()
    )

    assert limiter.allow(
        key="test",
        limit=2,
        window_seconds=60,
    )

    assert limiter.allow(
        key="test",
        limit=2,
        window_seconds=60,
    )

    assert not limiter.allow(
        key="test",
        limit=2,
        window_seconds=60,
    )


def test_beta_brute_force_is_limited(
    monkeypatch,
):
    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "correct-beta-code",
    )

    monkeypatch.setattr(
        main_module.settings,
        "access_failure_limit",
        2,
    )

    first = client.get(
        "/api/v1/teams",
        headers={
            "X-Beta-Access-Code": (
                "wrong-one"
            )
        },
    )

    second = client.get(
        "/api/v1/teams",
        headers={
            "X-Beta-Access-Code": (
                "wrong-two"
            )
        },
    )

    third = client.get(
        "/api/v1/teams",
        headers={
            "X-Beta-Access-Code": (
                "wrong-three"
            )
        },
    )

    assert (
        first.status_code
        == 401
    )

    assert (
        second.status_code
        == 401
    )

    assert (
        third.status_code
        == 429
    )

    assert (
        "Retry-After"
        in third.headers
    )


def test_ai_rate_limit_is_enforced(
    monkeypatch,
):
    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "",
    )

    monkeypatch.setattr(
        main_module.settings,
        "ai_rate_limit_per_minute",
        1,
    )

    first = client.post(
        "/api/v1/ai/analyse",
        json={},
    )

    second = client.post(
        "/api/v1/ai/analyse",
        json={},
    )

    assert (
        first.status_code
        != 429
    )

    assert (
        second.status_code
        == 429
    )


def test_correct_beta_code_is_not_blocked(
    monkeypatch,
):
    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "correct-beta-code",
    )

    monkeypatch.setattr(
        main_module.settings,
        "access_failure_limit",
        1,
    )

    response = client.get(
        "/api/v1/teams",
        headers={
            "X-Beta-Access-Code": (
                "correct-beta-code"
            )
        },
    )

    assert (
        response.status_code
        != 401
    )

    assert (
        response.status_code
        != 429
    )