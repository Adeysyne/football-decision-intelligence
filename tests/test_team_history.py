from fastapi.testclient import TestClient

from app.main import app
from tests.test_scenarios import (
    VALID_SCENARIO,
)


client = TestClient(
    app
)


def _create_team(
    team_name: str = "Sheffield FC",
) -> dict:
    response = client.post(
        "/api/v1/teams",
        json={
            "team_name": team_name,
            "default_formation": (
                "4-2-3-1"
            ),
            "tactical_identity": (
                "Balanced positional structure "
                "with controlled transitions."
            ),
        },
    )

    assert response.status_code == 201

    return response.json()


def _create_decision() -> dict:
    scenario = client.post(
        "/api/v1/scenarios",
        json=VALID_SCENARIO,
    )

    assert scenario.status_code == 201

    scenario_id = scenario.json()[
        "scenario_id"
    ]

    decision = client.post(
        f"/api/v1/decisions/"
        f"scenarios/{scenario_id}/analyse"
    )

    assert decision.status_code == 200

    return decision.json()


def test_team_profile_can_be_created_and_read():
    team = _create_team()

    response = client.get(
        f"/api/v1/teams/"
        f"{team['team_id']}"
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["team_name"]
        == "Sheffield FC"
    )

    assert (
        body["default_formation"]
        == "4-2-3-1"
    )


def test_duplicate_team_name_is_rejected():
    _create_team()

    response = client.post(
        "/api/v1/teams",
        json={
            "team_name": "Sheffield FC"
        },
    )

    assert response.status_code == 409


def test_new_team_history_starts_empty():
    team = _create_team()

    response = client.get(
        f"/api/v1/teams/"
        f"{team['team_id']}/"
        "history-summary"
    )

    assert response.status_code == 200

    body = response.json()

    assert body[
        "scenario_count"
    ] == 0

    assert body[
        "decision_count"
    ] == 0

    assert body[
        "outcome_count"
    ] == 0


def test_team_history_aggregates_feedback():
    team = _create_team()

    decision = _create_decision()

    decision_id = decision[
        "decision_id"
    ]

    leading_option_id = (
        decision[
            "decision_brief"
        ]["leading_option_id"]
    )

    selection = client.post(
        f"/api/v1/decisions/"
        f"{decision_id}/selection",
        json={
            "selected_option_id": (
                leading_option_id
            )
        },
    )

    assert selection.status_code == 200

    outcome = client.post(
        f"/api/v1/decisions/"
        f"{decision_id}/outcome",
        json={
            "final_our_score": 1,
            "final_opponent_score": 0,
            "coach_assessment": "helped",
            "outcome_summary": (
                "The team protected the lead "
                "after the intervention."
            ),
            "observed_effects": [
                "Wide exposure reduced."
            ],
        },
    )

    assert outcome.status_code == 200

    response = client.get(
        f"/api/v1/teams/"
        f"{team['team_id']}/"
        "history-summary"
    )

    assert response.status_code == 200

    body = response.json()

    assert body[
        "scenario_count"
    ] == 1

    assert body[
        "decision_count"
    ] == 1

    assert body[
        "selection_count"
    ] == 1

    assert body[
        "outcome_count"
    ] == 1

    assert body[
        "engine_leader_selected_count"
    ] == 1

    assert (
        body[
            "assessment_counts"
        ]["helped"]
        == 1
    )

    assert (
        body[
            "scenario_profile_counts"
        ]["protect_lead"]
        == 1
    )


def test_unknown_team_returns_404():
    response = client.get(
        "/api/v1/teams/"
        "11111111-1111-1111-1111-111111111111/"
        "history-summary"
    )

    assert response.status_code == 404