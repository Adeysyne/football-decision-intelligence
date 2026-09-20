from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_SCENARIO = {
    "team_name": "Sheffield FC",
    "opponent_name": "Example United",
    "minute": 68,
    "our_score": 1,
    "opponent_score": 0,
    "our_formation": "4-2-3-1",
    "opponent_formation": "4-3-3",
    "yellow_cards": ["Left-back"],
    "red_cards": [],
    "available_substitutions": [
        "Centre-back",
        "Left-back",
        "Defensive midfielder",
    ],
    "tactical_problem": (
        "Their right winger is repeatedly getting behind "
        "our left-back."
    ),
    "objective": (
        "Protect the lead without completely losing "
        "our attacking threat."
    ),
    "coach_observations": (
        "Our left-back is already booked and their "
        "right-back is beginning to overlap."
    ),
    "options": [],
    "requested_option_count": 3,
}


def test_create_scenario() -> None:
    response = client.post(
        "/api/v1/scenarios",
        json=VALID_SCENARIO,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "validated"
    assert body["next_step"] == "decision_engine"

    assert body["scenario"]["minute"] == 68
    assert body["scenario"]["our_score"] == 1
    assert body["scenario"]["opponent_score"] == 0

    assert "scenario_id" in body
    assert "created_at" in body


def test_invalid_match_minute_is_rejected() -> None:
    invalid_scenario = VALID_SCENARIO.copy()
    invalid_scenario["minute"] = 200

    response = client.post(
        "/api/v1/scenarios",
        json=invalid_scenario,
    )

    assert response.status_code == 422