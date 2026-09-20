from fastapi.testclient import TestClient

from app.main import app
from tests.test_scenarios import (
    VALID_SCENARIO,
)


client = TestClient(
    app
)


def _create_decision() -> dict:
    scenario_response = client.post(
        "/api/v1/scenarios",
        json=VALID_SCENARIO,
    )

    assert (
        scenario_response.status_code
        == 201
    )

    scenario_id = (
        scenario_response.json()[
            "scenario_id"
        ]
    )

    decision_response = client.post(
        f"/api/v1/decisions/"
        f"scenarios/{scenario_id}/analyse"
    )

    assert (
        decision_response.status_code
        == 200
    )

    return decision_response.json()


def test_coach_can_select_valid_option():
    decision = _create_decision()

    decision_id = decision[
        "decision_id"
    ]

    selected_option_id = (
        decision[
            "decision_brief"
        ]["options"][0]["option_id"]
    )

    response = client.post(
        f"/api/v1/decisions/"
        f"{decision_id}/selection",
        json={
            "selected_option_id": (
                selected_option_id
            ),
            "rationale": (
                "Best fit for the current "
                "match situation."
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["decision_id"]
        == decision_id
    )

    assert (
        body["selected_option_id"]
        == selected_option_id
    )


def test_invalid_option_is_rejected():
    decision = _create_decision()

    response = client.post(
        f"/api/v1/decisions/"
        f"{decision['decision_id']}/selection",
        json={
            "selected_option_id": (
                "option_999"
            )
        },
    )

    assert response.status_code == 422


def test_outcome_requires_selection():
    decision = _create_decision()

    response = client.post(
        f"/api/v1/decisions/"
        f"{decision['decision_id']}/outcome",
        json={
            "final_our_score": 1,
            "final_opponent_score": 0,
            "coach_assessment": "unclear",
            "outcome_summary": (
                "No coach selection had "
                "been recorded."
            ),
            "observed_effects": [],
        },
    )

    assert response.status_code == 409


def test_selection_and_outcome_round_trip():
    decision = _create_decision()

    decision_id = decision[
        "decision_id"
    ]

    selected_option_id = (
        decision[
            "decision_brief"
        ]["options"][0]["option_id"]
    )

    selection = client.post(
        f"/api/v1/decisions/"
        f"{decision_id}/selection",
        json={
            "selected_option_id": (
                selected_option_id
            ),
            "rationale": (
                "The coach preferred the "
                "lower-disruption option."
            ),
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
                "Fewer isolated wide duels.",
                "Attacking outlet remained available.",
            ],
            "next_time_notes": (
                "Monitor the threatened flank "
                "earlier."
            ),
        },
    )

    assert outcome.status_code == 200

    feedback = client.get(
        f"/api/v1/decisions/"
        f"{decision_id}/feedback"
    )

    assert feedback.status_code == 200

    body = feedback.json()

    assert (
        body["selection"][
            "selected_option_id"
        ]
        == selected_option_id
    )

    assert (
        body["outcome"][
            "coach_assessment"
        ]
        == "helped"
    )

    assert (
        body["outcome"][
            "final_our_score"
        ]
        == 1
    )


def test_duplicate_feedback_is_blocked():
    decision = _create_decision()

    decision_id = decision[
        "decision_id"
    ]

    selected_option_id = (
        decision[
            "decision_brief"
        ]["options"][0]["option_id"]
    )

    payload = {
        "selected_option_id": (
            selected_option_id
        )
    }

    first = client.post(
        f"/api/v1/decisions/"
        f"{decision_id}/selection",
        json=payload,
    )

    second = client.post(
        f"/api/v1/decisions/"
        f"{decision_id}/selection",
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 409