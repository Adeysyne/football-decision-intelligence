import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


BASE = {
    "team_name": "Test FC",
    "opponent_name": "Opponent FC",
    "our_formation": "4-2-3-1",
    "opponent_formation": "4-3-3",
    "yellow_cards": [],
    "red_cards": [],
    "available_substitutions": [
        "Centre-back",
        "Left-back",
        "Defensive midfielder",
        "Winger",
        "Striker",
    ],
    "options": [],
    "requested_option_count": 3,
}


EVALUATION_SCENARIOS = [
    {
        "name": "protect_lead",
        "expected_profile": "protect_lead",
        "data": {
            **BASE,
            "minute": 75,
            "our_score": 1,
            "opponent_score": 0,
            "yellow_cards": ["Left-back"],
            "tactical_problem": (
                "The opponent is creating repeated overloads "
                "on our left side."
            ),
            "objective": (
                "Protect the lead while keeping enough threat "
                "on the counter-attack."
            ),
            "coach_observations": (
                "Our left-back is booked and their right winger "
                "is repeatedly attacking that side."
            ),
        },
    },
    {
        "name": "chase_game",
        "expected_profile": "chase_game",
        "data": {
            **BASE,
            "minute": 72,
            "our_score": 0,
            "opponent_score": 1,
            "tactical_problem": (
                "We have possession but are struggling to create "
                "clear chances in the final third."
            ),
            "objective": (
                "Find an equaliser without becoming completely "
                "exposed to counter-attacks."
            ),
            "coach_observations": (
                "Our striker is isolated and our wide players "
                "are receiving the ball too far from goal."
            ),
        },
    },
    {
        "name": "control_midfield",
        "expected_profile": "control_game",
        "data": {
            **BASE,
            "minute": 55,
            "our_score": 1,
            "opponent_score": 1,
            "tactical_problem": (
                "We are being overrun in midfield and losing "
                "too many second balls."
            ),
            "objective": (
                "Control midfield and retain possession more "
                "consistently."
            ),
            "coach_observations": (
                "Their three central midfielders are creating "
                "numerical superiority against our midfield two."
            ),
        },
    },
    {
        "name": "balanced_game",
        "expected_profile": "balanced",
        "data": {
            **BASE,
            "minute": 35,
            "our_score": 0,
            "opponent_score": 0,
            "tactical_problem": (
                "The match is even and neither side is creating "
                "consistent high-quality openings."
            ),
            "objective": (
                "Improve our overall performance without taking "
                "unnecessary tactical risk."
            ),
            "coach_observations": (
                "Both teams are organised and possession is "
                "relatively balanced."
            ),
        },
    },
]


@pytest.mark.parametrize(
    "case",
    EVALUATION_SCENARIOS,
    ids=lambda case: case["name"],
)
def test_scenario_profile_detection(case) -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=case["data"],
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["scenario_profile"]
        == case["expected_profile"]
    )


@pytest.mark.parametrize(
    "case",
    EVALUATION_SCENARIOS,
    ids=lambda case: case["name"],
)
def test_all_evaluation_scenarios_produce_three_options(
    case,
) -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=case["data"],
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["options"]) == 3

    assert body["leading_option_id"] in {
        "option_1",
        "option_2",
        "option_3",
    }


@pytest.mark.parametrize(
    "case",
    EVALUATION_SCENARIOS,
    ids=lambda case: case["name"],
)
def test_weighted_scores_remain_valid(case) -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=case["data"],
    )

    assert response.status_code == 200

    body = response.json()

    for option in body["options"]:
        assert 1.0 <= option["weighted_score"] <= 5.0

        assert 8 <= option["total_score"] <= 40


def test_profiles_change_weight_priorities() -> None:
    protect = client.post(
        "/api/v1/decisions/analyse",
        json=EVALUATION_SCENARIOS[0]["data"],
    ).json()

    chase = client.post(
        "/api/v1/decisions/analyse",
        json=EVALUATION_SCENARIOS[1]["data"],
    ).json()

    control = client.post(
        "/api/v1/decisions/analyse",
        json=EVALUATION_SCENARIOS[2]["data"],
    ).json()

    assert (
        protect["score_weights"]["defensive_stability"]
        >
        protect["score_weights"]["attacking_threat"]
    )

    assert (
        chase["score_weights"]["attacking_threat"]
        >
        chase["score_weights"]["defensive_stability"]
    )

    assert (
        control["score_weights"]["midfield_control"]
        >
        control["score_weights"]["attacking_threat"]
    )