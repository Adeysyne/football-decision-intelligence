from fastapi.testclient import TestClient

from app.main import app
from tests.test_scenarios import (
    VALID_SCENARIO,
)


client = TestClient(
    app
)


def _create_scenario() -> dict:
    response = client.post(
        "/api/v1/scenarios",
        json=VALID_SCENARIO,
    )

    assert response.status_code == 201

    return response.json()


def test_saved_scenario_can_be_read():
    created = _create_scenario()

    response = client.get(
        f"/api/v1/scenarios/"
        f"{created['scenario_id']}"
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["scenario_id"]
        == created["scenario_id"]
    )

    assert (
        body["scenario"]["team_name"]
        == VALID_SCENARIO["team_name"]
    )


def test_scenario_history_returns_saved_scenario():
    created = _create_scenario()

    response = client.get(
        "/api/v1/scenarios",
        params={
            "team_name": (
                VALID_SCENARIO[
                    "team_name"
                ]
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1

    assert (
        body[0]["scenario_id"]
        == created["scenario_id"]
    )


def test_decision_is_persisted_for_saved_scenario():
    created = _create_scenario()

    scenario_id = created[
        "scenario_id"
    ]

    response = client.post(
        f"/api/v1/decisions/"
        f"scenarios/{scenario_id}/analyse"
    )

    assert response.status_code == 200

    decision = response.json()

    assert (
        decision["scenario_id"]
        == scenario_id
    )

    assert decision[
        "decision_id"
    ]

    assert (
        decision[
            "decision_brief"
        ]["leading_option_id"]
    )

    history = client.get(
        f"/api/v1/decisions/"
        f"scenarios/{scenario_id}"
    )

    assert history.status_code == 200

    history_body = history.json()

    assert len(
        history_body
    ) == 1

    assert (
        history_body[0][
            "decision_id"
        ]
        == decision[
            "decision_id"
        ]
    )


def test_unknown_scenario_returns_404():
    response = client.post(
        "/api/v1/decisions/"
        "scenarios/"
        "11111111-1111-1111-1111-111111111111/"
        "analyse"
    )

    assert response.status_code == 404