from copy import deepcopy

from app.models.decision import (
    DecisionBrief,
    DecisionScores,
    ScenarioProfile,
    TacticalOptionAnalysis,
)
from app.models.scenario import (
    ScenarioCreate,
    TacticalOptionInput,
)


SCORE_MIN = 1
SCORE_MAX = 5


BASE_SCORES = {
    "instruction": {
        "defensive_stability": 3,
        "attacking_threat": 4,
        "wide_area_control": 3,
        "midfield_control": 4,
        "transition_security": 3,
        "personnel_fit": 4,
        "tactical_continuity": 5,
        "objective_alignment": 3,
    },
    "personnel": {
        "defensive_stability": 3,
        "attacking_threat": 3,
        "wide_area_control": 3,
        "midfield_control": 3,
        "transition_security": 3,
        "personnel_fit": 4,
        "tactical_continuity": 4,
        "objective_alignment": 3,
    },
    "structural": {
        "defensive_stability": 4,
        "attacking_threat": 3,
        "wide_area_control": 4,
        "midfield_control": 3,
        "transition_security": 4,
        "personnel_fit": 3,
        "tactical_continuity": 2,
        "objective_alignment": 3,
    },
}


WEIGHT_PROFILES = {
    "balanced": {
        "defensive_stability": 1.0,
        "attacking_threat": 1.0,
        "wide_area_control": 1.0,
        "midfield_control": 1.0,
        "transition_security": 1.0,
        "personnel_fit": 1.0,
        "tactical_continuity": 1.0,
        "objective_alignment": 1.2,
    },
    "protect_lead": {
        "defensive_stability": 1.5,
        "attacking_threat": 0.7,
        "wide_area_control": 1.25,
        "midfield_control": 0.9,
        "transition_security": 1.4,
        "personnel_fit": 1.1,
        "tactical_continuity": 0.8,
        "objective_alignment": 1.5,
    },
    "chase_game": {
        "defensive_stability": 0.8,
        "attacking_threat": 1.7,
        "wide_area_control": 1.0,
        "midfield_control": 1.2,
        "transition_security": 0.9,
        "personnel_fit": 1.0,
        "tactical_continuity": 0.8,
        "objective_alignment": 1.6,
    },
    "control_game": {
        "defensive_stability": 1.0,
        "attacking_threat": 1.0,
        "wide_area_control": 1.0,
        "midfield_control": 1.6,
        "transition_security": 1.3,
        "personnel_fit": 0.9,
        "tactical_continuity": 1.2,
        "objective_alignment": 1.5,
    },
}


DEFENSIVE_TERMS = (
    "centre-back",
    "center-back",
    "defender",
    "defensive",
    "left-back",
    "right-back",
    "full-back",
)

ATTACKING_TERMS = (
    "striker",
    "forward",
    "winger",
    "attacking midfielder",
    "number 10",
)

MIDFIELD_TERMS = (
    "central midfielder",
    "defensive midfielder",
    "attacking midfielder",
    "midfielder",
)


def _clamp(value: int) -> int:
    return max(
        SCORE_MIN,
        min(SCORE_MAX, value),
    )


def _has_any(
    text: str,
    terms: tuple[str, ...],
) -> bool:
    text = text.lower()
    return any(
        term in text
        for term in terms
    )


def _scenario_text(
    scenario: ScenarioCreate,
) -> str:
    return " ".join(
        [
            scenario.tactical_problem,
            scenario.objective,
            scenario.coach_observations or "",
            " ".join(scenario.yellow_cards),
            " ".join(
                scenario.available_substitutions
            ),
        ]
    ).lower()


def _detect_context(
    scenario: ScenarioCreate,
) -> dict[str, bool]:
    text = _scenario_text(scenario)

    wide_terms = (
        "wing",
        "winger",
        "wide",
        "flank",
        "overlap",
        "full-back",
        "left-back",
        "right-back",
    )

    protect_terms = (
        "protect",
        "hold the lead",
        "defend the lead",
        "see out",
        "preserve the lead",
    )

    attack_terms = (
        "equalise",
        "equalize",
        "chase the game",
        "need a goal",
        "find an equaliser",
        "find an equalizer",
        "create more chances",
    )

    control_terms = (
        "control possession",
        "control the game",
        "control midfield",
        "retain possession",
        "keep possession",
        "midfield control",
        "overrun in midfield",
        "second balls",
    )

    booked_defender = any(
        _has_any(
            card,
            DEFENSIVE_TERMS,
        )
        for card in scenario.yellow_cards
    )

    defensive_sub_available = any(
        _has_any(
            substitute,
            DEFENSIVE_TERMS,
        )
        for substitute
        in scenario.available_substitutions
    )

    attacking_sub_available = any(
        _has_any(
            substitute,
            ATTACKING_TERMS,
        )
        for substitute
        in scenario.available_substitutions
    )

    midfield_sub_available = any(
        _has_any(
            substitute,
            MIDFIELD_TERMS,
        )
        for substitute
        in scenario.available_substitutions
    )

    return {
        "wide_threat": _has_any(
            text,
            wide_terms,
        ),
        "booked_defender": booked_defender,
        "defensive_sub_available":
            defensive_sub_available,
        "attacking_sub_available":
            attacking_sub_available,
        "midfield_sub_available":
            midfield_sub_available,
        "protecting_lead": (
            scenario.our_score
            > scenario.opponent_score
            and _has_any(
                text,
                protect_terms,
            )
        ),
        "chasing_game": (
            scenario.our_score
            < scenario.opponent_score
            or _has_any(
                text,
                attack_terms,
            )
        ),
        "control_game": _has_any(
            text,
            control_terms,
        ),
    }


def _scenario_profile(
    scenario: ScenarioCreate,
) -> ScenarioProfile:
    context = _detect_context(scenario)

    if context["protecting_lead"]:
        return "protect_lead"

    if context["chasing_game"]:
        return "chase_game"

    if context["control_game"]:
        return "control_game"

    return "balanced"


def _generate_engine_options(
    scenario: ScenarioCreate,
) -> list[TacticalOptionInput]:
    profile = _scenario_profile(
        scenario
    )

    context = _detect_context(
        scenario
    )

    if profile == "protect_lead":
        options = [
            (
                "Keep shape and add defensive support",
                (
                    f"Remain in {scenario.our_formation}, "
                    "increase support around the threatened "
                    "area and protect vulnerable duels."
                ),
            ),
            (
                "Make a targeted defensive personnel change",
                (
                    "Replace or protect the vulnerable "
                    "defensive player while preserving "
                    "the overall structure."
                    if context["booked_defender"]
                    else
                    "Introduce a suitable defensive player "
                    "while preserving the overall structure."
                ),
            ),
            (
                "Use a more conservative structure",
                (
                    "Create an additional defensive layer "
                    "and reduce transition exposure."
                ),
            ),
        ]

    elif profile == "chase_game":
        options = [
            (
                "Increase attacking support within the current shape",
                (
                    f"Keep {scenario.our_formation} but move "
                    "supporting players closer to the final line."
                ),
            ),
            (
                "Introduce an attacking player",
                (
                    "Make a targeted attacking personnel "
                    "change to increase threat in the final third."
                ),
            ),
            (
                "Use a more attacking structure",
                (
                    "Restructure the team to commit an "
                    "additional player to attacking areas, "
                    "accepting greater transition exposure."
                ),
            ),
        ]

    elif profile == "control_game":
        options = [
            (
                "Increase midfield support within the current shape",
                (
                    f"Keep {scenario.our_formation} but improve "
                    "midfield spacing and support."
                ),
            ),
            (
                "Introduce an additional midfielder",
                (
                    "Use a targeted personnel change to improve "
                    "central numbers and second-ball coverage."
                ),
            ),
            (
                "Restructure to create an extra midfield presence",
                (
                    "Change the structure to create greater "
                    "central numerical support and control."
                ),
            ),
        ]

    else:
        options = [
            (
                "Adjust instructions within the current shape",
                (
                    f"Keep {scenario.our_formation} and make "
                    "measured role or positioning adjustments."
                ),
            ),
            (
                "Make a targeted personnel change",
                (
                    "Use one substitution to address the "
                    "clearest individual mismatch."
                ),
            ),
            (
                "Make a measured structural adjustment",
                (
                    "Change the structure modestly to improve "
                    "collective balance."
                ),
            ),
        ]

    return [
        TacticalOptionInput(
            label=label,
            description=description,
        )
        for label, description
        in options[
            :scenario.requested_option_count
        ]
    ]


def _classify_option(
    option: TacticalOptionInput,
) -> str:
    text = (
        f"{option.label} "
        f"{option.description}"
    ).lower()

    personnel_terms = (
        "replace",
        "substitute",
        "substitution",
        "bring on",
        "personnel",
        "introduce",
    )

    structural_terms = (
        "formation",
        "back five",
        "5-4-1",
        "5-3-2",
        "structure",
        "structural",
        "system",
        "extra midfield presence",
    )

    if _has_any(
        text,
        personnel_terms,
    ):
        return "personnel"

    if _has_any(
        text,
        structural_terms,
    ):
        return "structural"

    return "instruction"


def _score_option(
    category: str,
    scenario: ScenarioCreate,
) -> DecisionScores:
    context = _detect_context(
        scenario
    )

    profile = _scenario_profile(
        scenario
    )

    scores = deepcopy(
        BASE_SCORES[category]
    )

    if context["wide_threat"]:
        scores["wide_area_control"] += 1

    if context["booked_defender"]:
        if category == "personnel":
            scores["personnel_fit"] += 1
            scores["defensive_stability"] += 1
            scores["objective_alignment"] += 2

        elif category == "instruction":
            scores["personnel_fit"] -= 1

    if (
        category == "personnel"
        and profile == "protect_lead"
        and not context[
            "defensive_sub_available"
        ]
    ):
        scores["personnel_fit"] -= 1

    if profile == "protect_lead":
        if category == "structural":
            scores[
                "defensive_stability"
            ] += 1

            scores[
                "transition_security"
            ] += 1

        elif category == "personnel":
            scores[
                "objective_alignment"
            ] += 1

    elif profile == "chase_game":
        if category == "instruction":
            scores[
                "attacking_threat"
            ] += 1

            scores[
                "objective_alignment"
            ] += 1

        elif (
            category == "personnel"
            and context[
                "attacking_sub_available"
            ]
        ):
            scores[
                "attacking_threat"
            ] += 2

            scores[
                "objective_alignment"
            ] += 1

        elif category == "structural":
            scores[
                "attacking_threat"
            ] += 2

            scores[
                "objective_alignment"
            ] += 2

            scores[
                "defensive_stability"
            ] -= 1

    elif profile == "control_game":
        if category == "instruction":
            scores[
                "midfield_control"
            ] += 1

            scores[
                "objective_alignment"
            ] += 1

        elif (
            category == "personnel"
            and context[
                "midfield_sub_available"
            ]
        ):
            scores[
                "midfield_control"
            ] += 1

            scores[
                "objective_alignment"
            ] += 1

        elif category == "structural":
            scores[
                "midfield_control"
            ] += 2

            scores[
                "transition_security"
            ] += 1

            scores[
                "objective_alignment"
            ] += 2

    clamped_scores = {
        key: _clamp(value)
        for key, value
        in scores.items()
    }

    return DecisionScores(
        **clamped_scores
    )


def _weighted_score(
    scores: DecisionScores,
    profile: ScenarioProfile,
) -> float:
    values = scores.model_dump()

    weights = WEIGHT_PROFILES[
        profile
    ]

    weighted_total = sum(
        values[key] * weights[key]
        for key in values
    )

    total_weight = sum(
        weights.values()
    )

    return round(
        weighted_total
        / total_weight,
        2,
    )


def _strengths(
    category: str,
    scenario: ScenarioCreate,
) -> list[str]:
    profile = _scenario_profile(
        scenario
    )

    if category == "instruction":
        return [
            "Preserves tactical familiarity.",
            (
                "Requires relatively little "
                "structural disruption."
            ),
        ]

    if category == "personnel":
        return [
            "Targets a specific problem.",
            (
                "Preserves much of the existing "
                "team structure."
            ),
        ]

    if profile == "protect_lead":
        return [
            "Provides stronger defensive protection.",
            "Improves transition security.",
        ]

    if profile == "chase_game":
        return [
            (
                "Commits more players to "
                "attacking areas."
            ),
            (
                "Changes the attacking picture "
                "more aggressively."
            ),
        ]

    if profile == "control_game":
        return [
            (
                "Creates greater midfield presence."
            ),
            (
                "Can improve central control and "
                "second-ball coverage."
            ),
        ]

    return [
        (
            "Can solve a structural problem that "
            "instructions alone may not fix."
        )
    ]


def _risks(
    category: str,
    scenario: ScenarioCreate,
) -> list[str]:
    profile = _scenario_profile(
        scenario
    )

    if category == "instruction":
        return [
            (
                "The underlying personnel or "
                "structural problem may remain."
            )
        ]

    if category == "personnel":
        return [
            (
                "The replacement may not reproduce "
                "the outgoing player's qualities."
            ),
            (
                "A substitution reduces remaining options."
            ),
        ]

    if profile == "protect_lead":
        return [
            "May reduce attacking presence.",
            "The team may become too passive.",
        ]

    if profile == "chase_game":
        return [
            (
                "Greater attacking commitment can "
                "increase counter-attacking exposure."
            )
        ]

    if profile == "control_game":
        return [
            (
                "Structural change may temporarily "
                "disrupt pressing and width."
            )
        ]

    return [
        (
            "Structural change can create "
            "coordination problems."
        )
    ]


def _assumptions(
    category: str,
) -> list[str]:
    category_assumption = {
        "instruction": (
            "Players can adapt their responsibilities "
            "without losing coordination."
        ),
        "personnel": (
            "A suitable replacement is available "
            "and physically ready."
        ),
        "structural": (
            "The team can execute the structural "
            "adjustment with sufficient familiarity."
        ),
    }

    return [
        (
            "The analysis is based only on information "
            "supplied by the coach."
        ),
        (
            "No professional tracking data is being "
            "used at this stage."
        ),
        category_assumption[category],
    ]


def _analyse_option(
    option: TacticalOptionInput,
    index: int,
    scenario: ScenarioCreate,
    profile: ScenarioProfile,
) -> TacticalOptionAnalysis:
    category = _classify_option(
        option
    )

    scores = _score_option(
        category,
        scenario,
    )

    total_score = sum(
        scores.model_dump().values()
    )

    return TacticalOptionAnalysis(
        option_id=f"option_{index}",
        label=option.label,
        description=option.description,
        category=category,
        scores=scores,
        total_score=total_score,
        weighted_score=_weighted_score(
            scores,
            profile,
        ),
        strengths=_strengths(
            category,
            scenario,
        ),
        risks=_risks(
            category,
            scenario,
        ),
        assumptions=_assumptions(
            category
        ),
    )


def _leading_reason(
    option: TacticalOptionAnalysis,
    profile: ScenarioProfile,
) -> str:
    reasons = {
        "protect_lead": (
            "defensive stability, transition security "
            "and protecting the current result"
        ),
        "chase_game": (
            "attacking threat and improving goal creation"
        ),
        "control_game": (
            "midfield control, possession stability "
            "and transition management"
        ),
        "balanced": (
            "a broadly balanced set of tactical priorities"
        ),
    }

    return (
        f"{option.label} currently has the highest "
        f"objective-aware weighted score "
        f"({option.weighted_score}/5) because the "
        f"scenario prioritises {reasons[profile]}. "
        "This is a decision-support ranking, not a "
        "claim that the option is objectively correct."
    )


def _main_tradeoff(
    category: str,
    profile: ScenarioProfile,
) -> str:
    if (
        profile == "protect_lead"
        and category == "personnel"
    ):
        return (
            "A targeted personnel change can remove "
            "a specific risk while preserving structure, "
            "but it uses a substitution."
        )

    if profile == "chase_game":
        return (
            "Increasing attacking presence may improve "
            "chance creation but can increase transition exposure."
        )

    if profile == "control_game":
        return (
            "Greater midfield presence can improve control "
            "but may temporarily disrupt existing team relationships."
        )

    return (
        "The leading option offers the best current balance, "
        "while alternatives retain different tactical advantages."
    )


def _monitor_next(
    scenario: ScenarioCreate,
) -> list[str]:
    context = _detect_context(
        scenario
    )

    items = [
        (
            "Whether the original tactical problem "
            "continues after the intervention."
        ),
        (
            "Whether the change damages the team's "
            "ability to progress the ball."
        ),
    ]

    if context["wide_threat"]:
        items.append(
            (
                "Repeated overloads, overlaps or 2v1 "
                "situations on the threatened flank."
            )
        )

    if context["booked_defender"]:
        items.append(
            (
                "Whether the booked defender is still "
                "being isolated into repeated duels."
            )
        )

    if context["protecting_lead"]:
        items.append(
            (
                "Whether the team becomes too deep and "
                "loses counter-attacking outlets."
            )
        )

    if context["chasing_game"]:
        items.append(
            (
                "Whether the intervention creates more "
                "entries into dangerous attacking areas."
            )
        )

    if context["control_game"]:
        items.append(
            (
                "Whether midfield possession and "
                "second-ball control improve."
            )
        )

    return items


def _confidence(
    scenario: ScenarioCreate,
) -> str:
    evidence_points = sum(
        [
            bool(
                scenario.opponent_formation
            ),
            bool(
                scenario.coach_observations
            ),
            bool(
                scenario.available_substitutions
            ),
            bool(
                scenario.yellow_cards
                or scenario.red_cards
            ),
        ]
    )

    if evidence_points >= 3:
        return "medium"

    return "low"


def build_decision_brief(
    scenario: ScenarioCreate,
) -> DecisionBrief:
    profile = _scenario_profile(
        scenario
    )

    if scenario.options:
        source = "coach_options"
        options = scenario.options
    else:
        source = "engine_options"
        options = _generate_engine_options(
            scenario
        )

    analysed_options = [
        _analyse_option(
            option=option,
            index=index,
            scenario=scenario,
            profile=profile,
        )
        for index, option
        in enumerate(
            options,
            start=1,
        )
    ]

    leading_option = max(
        analysed_options,
        key=lambda item: (
            item.weighted_score,
            item.total_score,
        ),
    )

    scenario_summary = (
        f"{scenario.team_name} vs "
        f"{scenario.opponent_name or 'opponent'}: "
        f"{scenario.our_score}-"
        f"{scenario.opponent_score} "
        f"at minute {scenario.minute}. "
        f"Problem: {scenario.tactical_problem}"
    )

    return DecisionBrief(
        scenario_summary=scenario_summary,
        scenario_profile=profile,
        generated_from=source,
        score_weights=
            WEIGHT_PROFILES[profile],
        options=analysed_options,
        leading_option_id=
            leading_option.option_id,
        leading_option_reason=
            _leading_reason(
                leading_option,
                profile,
            ),
        main_tradeoff=
            _main_tradeoff(
                leading_option.category,
                profile,
            ),
        monitor_next=
            _monitor_next(
                scenario
            ),
        confidence=
            _confidence(
                scenario
            ),
        scoring_note=(
            "Raw dimension scores use a transparent "
            "1-5 rule-based scale. Weighted scores "
            "change dimension importance according "
            "to the detected objective. They are "
            "decision-support signals, not probabilities "
            "or claims of objective tactical truth."
        ),
        coach_decision_required=True,
    )