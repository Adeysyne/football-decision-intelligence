from app.models.scenario import ScenarioCreate
from app.services.decision_engine import build_decision_brief


SCENARIOS = [
    {
        "name": "Protect lead / wide overload",
        "data": {
            "team_name": "Test FC",
            "opponent_name": "Opponent FC",
            "minute": 75,
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
                "The opponent is repeatedly overloading our left side."
            ),
            "objective": (
                "Protect the lead while retaining enough counter-attacking threat."
            ),
            "coach_observations": (
                "Our left-back is booked and their right winger "
                "is repeatedly attacking that side."
            ),
            "options": [],
            "requested_option_count": 3,
        },
    },
    {
        "name": "Chase equaliser",
        "data": {
            "team_name": "Test FC",
            "opponent_name": "Opponent FC",
            "minute": 72,
            "our_score": 0,
            "opponent_score": 1,
            "our_formation": "4-2-3-1",
            "opponent_formation": "4-3-3",
            "yellow_cards": [],
            "red_cards": [],
            "available_substitutions": [
                "Winger",
                "Striker",
                "Attacking midfielder",
            ],
            "tactical_problem": (
                "We have possession but are struggling to create "
                "clear chances in the final third."
            ),
            "objective": (
                "Find an equaliser while maintaining enough security "
                "against counter-attacks."
            ),
            "coach_observations": (
                "Our striker is isolated and our wide players "
                "are receiving too far from goal."
            ),
            "options": [],
            "requested_option_count": 3,
        },
    },
    {
        "name": "Control midfield",
        "data": {
            "team_name": "Test FC",
            "opponent_name": "Opponent FC",
            "minute": 55,
            "our_score": 1,
            "opponent_score": 1,
            "our_formation": "4-2-3-1",
            "opponent_formation": "4-3-3",
            "yellow_cards": [],
            "red_cards": [],
            "available_substitutions": [
                "Central midfielder",
                "Defensive midfielder",
                "Winger",
            ],
            "tactical_problem": (
                "We are being overrun in midfield and losing too "
                "many second balls."
            ),
            "objective": (
                "Control midfield and retain possession more consistently."
            ),
            "coach_observations": (
                "Their midfield three are creating numerical superiority "
                "against our midfield two."
            ),
            "options": [],
            "requested_option_count": 3,
        },
    },
    {
        "name": "Balanced game",
        "data": {
            "team_name": "Test FC",
            "opponent_name": "Opponent FC",
            "minute": 35,
            "our_score": 0,
            "opponent_score": 0,
            "our_formation": "4-2-3-1",
            "opponent_formation": "4-3-3",
            "yellow_cards": [],
            "red_cards": [],
            "available_substitutions": [
                "Central midfielder",
                "Winger",
                "Striker",
            ],
            "tactical_problem": (
                "The match is even and neither side is creating "
                "consistent high-quality openings."
            ),
            "objective": (
                "Improve overall performance without taking "
                "unnecessary tactical risk."
            ),
            "coach_observations": (
                "Both teams are organised and possession is balanced."
            ),
            "options": [],
            "requested_option_count": 3,
        },
    },
]


for case in SCENARIOS:
    scenario = ScenarioCreate(**case["data"])
    brief = build_decision_brief(scenario)

    print("=" * 72)
    print(case["name"])
    print(f"Profile: {brief.scenario_profile}")
    print()

    for option in brief.options:
        marker = (
            " <-- LEADING"
            if option.option_id == brief.leading_option_id
            else ""
        )

        print(
            f"{option.option_id}: "
            f"{option.label} | "
            f"{option.weighted_score:.2f}/5"
            f"{marker}"
        )

    print()