from copy import deepcopy

from app.models.scenario import ScenarioCreate
from app.services.decision_engine import build_decision_brief
from tests.test_decision_engine import BASE_SCENARIO


def _labels(brief) -> list[str]:
    return [
        option.label
        for option in brief.options
    ]


def _personnel_options(brief):
    return [
        option
        for option in brief.options
        if option.category == "personnel"
    ]


def test_no_substitutions_excludes_personnel_options() -> None:
    """
    Founder-evidence regression for controlled Scenario B.

    If no substitutions remain, engine-generated alternatives must not
    present a substitution-dependent personnel action as feasible.
    """

    data = deepcopy(BASE_SCENARIO)

    data["minute"] = 68
    data["our_score"] = 1
    data["opponent_score"] = 0

    data["our_formation"] = "4-2-3-1"
    data["opponent_formation"] = "4-3-3"

    data["yellow_cards"] = [
        "Left-back",
    ]

    data["red_cards"] = []

    data["available_substitutions"] = []

    data["tactical_problem"] = (
        "Their right winger repeatedly gets behind "
        "our left-back."
    )

    data["objective"] = (
        "Protect the lead while retaining "
        "an attacking outlet."
    )

    data["coach_observations"] = (
        "INTERNAL SYNTHETIC TEST. "
        "No substitutions remain. "
        "Player abilities beyond their roles are unknown."
    )

    data["options"] = []
    data["requested_option_count"] = 3

    brief = build_decision_brief(
        ScenarioCreate(**data)
    )

    assert brief.scenario_profile == "protect_lead"

    assert not _personnel_options(brief), (
        "Engine generated a substitution-dependent personnel "
        "option even though no substitutions remained. "
        f"Generated options: {_labels(brief)}"
    )

    leading = next(
        option
        for option in brief.options
        if option.option_id == brief.leading_option_id
    )

    assert leading.category != "personnel"


def test_chase_game_does_not_offer_unavailable_attacking_sub() -> None:
    """
    Founder-evidence regression for controlled Scenario C.

    A chase-game scenario must not generate 'Introduce an attacking
    player' when the supplied bench contains no attacking role.
    """

    data = deepcopy(BASE_SCENARIO)

    data["minute"] = 75
    data["our_score"] = 0
    data["opponent_score"] = 1

    data["our_formation"] = "4-2-3-1"
    data["opponent_formation"] = "4-3-3"

    data["yellow_cards"] = [
        "Left-back",
    ]

    data["red_cards"] = []

    data["available_substitutions"] = [
        "Centre-back",
        "Left-back",
        "Defensive midfielder",
    ]

    data["tactical_problem"] = (
        "Their right winger repeatedly gets behind "
        "our left-back."
    )

    data["objective"] = (
        "Seek an equaliser while managing "
        "counterattack exposure."
    )

    data["coach_observations"] = (
        "INTERNAL SYNTHETIC TEST. "
        "Two substitutions remain. "
        "Player abilities beyond their roles are unknown."
    )

    data["options"] = []
    data["requested_option_count"] = 3

    brief = build_decision_brief(
        ScenarioCreate(**data)
    )

    assert brief.scenario_profile == "chase_game"

    labels = _labels(brief)

    assert (
        "Introduce an attacking player"
        not in labels
    ), (
        "Engine offered an attacking personnel substitution "
        "despite no attacking substitute being supplied. "
        f"Generated options: {labels}"
    )


def test_chase_game_can_offer_attacking_sub_when_available() -> None:
    """
    Positive control: the feasibility rule must not remove the
    attacking personnel option when an attacking substitute exists.
    """

    data = deepcopy(BASE_SCENARIO)

    data["minute"] = 75
    data["our_score"] = 0
    data["opponent_score"] = 1

    data["available_substitutions"] = [
        "Centre-back",
        "Winger",
        "Striker",
    ]

    data["tactical_problem"] = (
        "We need greater threat in the final third."
    )

    data["objective"] = (
        "Seek an equaliser while managing "
        "counterattack exposure."
    )

    data["coach_observations"] = (
        "Two substitutions remain."
    )

    data["options"] = []
    data["requested_option_count"] = 3

    brief = build_decision_brief(
        ScenarioCreate(**data)
    )

    assert brief.scenario_profile == "chase_game"

    assert (
        "Introduce an attacking player"
        in _labels(brief)
    )