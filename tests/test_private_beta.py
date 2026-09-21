import importlib

from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app
)


def test_pilot_interest_is_recorded():
    response = client.post(
        "/api/v1/pilot-interest",
        json={
            "coach_name": (
                "Test Coach"
            ),
            "email": (
                "coach@example.com"
            ),
            "club_or_team": (
                "Pilot FC"
            ),
            "role": (
                "Head Coach"
            ),
            "would_use_in_real_matches": (
                "yes"
            ),
            "join_private_pilot": (
                "yes"
            ),
            "willingness_to_pay_monthly_gbp": (
                25
            ),
            "most_valuable_feature": (
                "Verified tactical comparisons."
            ),
            "feedback": (
                "Keep the match workflow fast."
            ),
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert (
        body["status"]
        == "recorded"
    )

    assert (
        body[
            "willingness_to_pay_monthly_gbp"
        ]
        == 25
    )

    assert (
        body[
            "join_private_pilot"
        ]
        == "yes"
    )

    assert (
        body[
            "pilot_interest_id"
        ]
    )


def test_invalid_pilot_answer_is_rejected():
    response = client.post(
        "/api/v1/pilot-interest",
        json={
            "coach_name": (
                "Test Coach"
            ),
            "email": (
                "coach@example.com"
            ),
            "club_or_team": (
                "Pilot FC"
            ),
            "role": (
                "Head Coach"
            ),
            "would_use_in_real_matches": (
                "definitely"
            ),
            "join_private_pilot": (
                "yes"
            ),
        },
    )

    assert response.status_code == 422


def test_private_beta_rejects_missing_code(
    monkeypatch,
):
    main_module = importlib.import_module(
        "app.main"
    )

    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "test-private-code",
    )

    response = client.get(
        "/api/v1/teams"
    )

    assert response.status_code == 401

    assert (
        response.json()["detail"]
        == "Private beta access code required."
    )


def test_private_beta_rejects_wrong_code(
    monkeypatch,
):
    main_module = importlib.import_module(
        "app.main"
    )

    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "test-private-code",
    )

    response = client.get(
        "/api/v1/teams",
        headers={
            "X-Beta-Access-Code": (
                "wrong-code"
            )
        },
    )

    assert response.status_code == 401


def test_private_beta_accepts_correct_code(
    monkeypatch,
):
    main_module = importlib.import_module(
        "app.main"
    )

    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "test-private-code",
    )

    response = client.get(
        "/api/v1/teams",
        headers={
            "X-Beta-Access-Code": (
                "test-private-code"
            )
        },
    )

    assert response.status_code == 200