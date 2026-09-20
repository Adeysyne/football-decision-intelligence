from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


BASE_SCENARIO = {
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


def test_decision_engine_generates_options() -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=BASE_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["generated_from"] == "engine_options"

    assert len(body["options"]) == 3

    assert body["coach_decision_required"] is True

    assert body["confidence"] in {
        "low",
        "medium",
    }

    assert body["leading_option_id"] in {
        "option_1",
        "option_2",
        "option_3",
    }


def test_all_scores_are_between_one_and_five() -> None:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=BASE_SCENARIO,
    )

    assert response.status_code == 200

    body = response.json()

    for option in body["options"]:
        for score in option["scores"].values():
            assert 1 <= score <= 5


def test_coach_supplied_options_are_used() -> None:
    scenario = BASE_SCENARIO.copy()

    scenario["options"] = [
        {
            "label": "Keep current shape",
            "description": (
                "Remain in the current formation "
                "and increase wide defensive support."
            ),
        },
        {
            "label": "Replace the booked left-back",
            "description": (
                "Make a defensive substitution "
                "while preserving the team structure."
            ),
        },
    ]

    response = client.post(
        "/api/v1/decisions/analyse",
        json=scenario,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["generated_from"] == "coach_options"

    assert len(body["options"]) == 2