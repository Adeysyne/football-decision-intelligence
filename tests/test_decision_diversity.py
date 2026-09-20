from fastapi.testclient import TestClient

from app.main import app
from tests.test_tactical_evaluation_set import (
    EVALUATION_SCENARIOS,
)


client = TestClient(app)


EXPECTED_LEADERS = {
    "protect_lead": "option_2",
    "chase_game": "option_1",
    "control_midfield": "option_3",
    "balanced_game": "option_1",
}


def test_engine_does_not_default_to_one_option() -> None:
    observed_leaders = set()

    for case in EVALUATION_SCENARIOS:
        response = client.post(
            "/api/v1/decisions/analyse",
            json=case["data"],
        )

        assert response.status_code == 200

        body = response.json()

        expected = EXPECTED_LEADERS[
            case["name"]
        ]

        assert (
            body["leading_option_id"]
            == expected
        )

        observed_leaders.add(
            body["leading_option_id"]
        )

    assert len(observed_leaders) >= 3