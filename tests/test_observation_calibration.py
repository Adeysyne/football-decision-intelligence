from copy import deepcopy

from fastapi.testclient import TestClient

from app.main import app
from tests.test_objective_weighting import (
    PROTECT_LEAD_SCENARIO,
)


client = TestClient(app)


def _analyse(scenario: dict) -> dict:
    response = client.post(
        "/api/v1/decisions/analyse",
        json=scenario,
    )

    assert response.status_code == 200

    return response.json()


def _option(
    brief: dict,
    label: str,
) -> dict:
    return next(
        option
        for option in brief["options"]
        if option["label"] == label
    )


def test_positive_current_match_evidence_tempers_booking_bias() -> None:
    scenario = deepcopy(
        PROTECT_LEAD_SCENARIO
    )

    scenario["tactical_problem"] = (
        "Their right winger remains the main threat "
        "down our left side."
    )

    scenario["objective"] = (
        "Protect the lead while retaining control "
        "and an attacking outlet."
    )

    scenario["coach_observations"] = (
        "The left-back has kept the opponent's right "
        "winger under control for the first 68 minutes "
        "despite being on a yellow card."
    )

    brief = _analyse(scenario)

    keep_shape = _option(
        brief,
        "Keep shape and add defensive support",
    )

    personnel = _option(
        brief,
        "Make a targeted defensive personnel change",
    )

    assert (
        keep_shape["weighted_score"]
        > personnel["weighted_score"]
    )

    assert (
        brief["leading_option_id"]
        == keep_shape["option_id"]
    )


def test_negative_current_match_evidence_supports_personnel_response() -> None:
    scenario = deepcopy(
        PROTECT_LEAD_SCENARIO
    )

    scenario["coach_observations"] = (
        "Our booked left-back is getting beaten "
        "repeatedly and is struggling to contain "
        "the opponent's right winger."
    )

    brief = _analyse(scenario)

    keep_shape = _option(
        brief,
        "Keep shape and add defensive support",
    )

    personnel = _option(
        brief,
        "Make a targeted defensive personnel change",
    )

    assert (
        personnel["weighted_score"]
        > keep_shape["weighted_score"]
    )

    assert (
        brief["leading_option_id"]
        == personnel["option_id"]
    )


def test_ambiguous_observation_preserves_existing_baseline() -> None:
    scenario = deepcopy(
        PROTECT_LEAD_SCENARIO
    )

    # This observation identifies risk but does not state whether
    # the defender is currently succeeding or failing.
    scenario["coach_observations"] = (
        "Our left-back is already booked and their "
        "right-back is beginning to overlap."
    )

    brief = _analyse(scenario)

    personnel = _option(
        brief,
        "Make a targeted defensive personnel change",
    )

    assert (
        brief["leading_option_id"]
        == personnel["option_id"]
    )
