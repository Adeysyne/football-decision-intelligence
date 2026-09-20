from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


PROTECT_LEAD_SCENARIO = {
    "team_name": "Sheffield FC",
    "opponent_name": "Example United",
    "minute": 68,
    "our_score": 1,
    "opponent_score": 0,
    "our_formation": "4-2-3-1",
    "opponent_formation": "4-3-3",
    "yellow_cards": [
        "Left-back"
    ],
    "red_cards": [],
    "available_substitutions": [
        "Centre-back",
        "Left-back",
        "Defensive midfielder",
    ],
    "tactical_problem": (
        "Their right winger is repeatedly getting "
        "behind our left-back."
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


def test_protect_lead_profile() -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=PROTECT_LEAD_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["scenario_profile"] == "protect_lead"

    assert (
        body["score_weights"]["defensive_stability"]
        >
        body["score_weights"]["attacking_threat"]
    )

    for option in body["options"]:
        assert 1.0 <= option["weighted_score"] <= 5.0


def test_protect_lead_prefers_targeted_change() -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=PROTECT_LEAD_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["leading_option_id"] == "option_2"


def test_chase_game_changes_weight_profile() -> None:
    scenario = PROTECT_LEAD_SCENARIO.copy()

    scenario["our_score"] = 0
    scenario["opponent_score"] = 1
    scenario["yellow_cards"] = []
    scenario["tactical_problem"] = (
        "We are struggling to create enough dangerous "
        "attacking situations."
    )
    scenario["objective"] = (
        "Find an equaliser while maintaining enough "
        "security against counter-attacks."
    )
    scenario["coach_observations"] = (
        "We have possession but are not creating enough "
        "chances in the final third."
    )

    response = client.post(
        "/api/v1/decisions/analyse",
        json=scenario,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["scenario_profile"] == "chase_game"

    assert (
        body["score_weights"]["attacking_threat"]
        >
        body["score_weights"]["defensive_stability"]
    )


def test_weighted_score_is_explained() -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=PROTECT_LEAD_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    assert "weighted score" in (
        body["leading_option_reason"].lower()
    )

    assert "not probabilities" in (
        body["scoring_note"].lower()
    )