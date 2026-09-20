from collections.abc import Iterable

from app.models.decision import DecisionBrief, ScenarioProfile
from app.models.scenario import ScenarioCreate
from app.models.tactical_knowledge import (
    RetrievedTacticalKnowledge,
    TacticalKnowledgeItem,
)


KNOWLEDGE_BASE: tuple[TacticalKnowledgeItem, ...] = (
    TacticalKnowledgeItem(
        knowledge_id="protect_lead_001",
        title="Preserve an attacking outlet",
        principle=(
            "When protecting a lead, additional defensive security "
            "should be balanced against the risk of becoming so deep "
            "that the team loses useful attacking or counter-attacking "
            "outlets."
        ),
        caveat=(
            "The appropriate balance depends on the actual pressure, "
            "player roles and match context supplied by the coach."
        ),
        tags=[
            "profile:protect_lead",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="protect_lead_002",
        title="Reduce repeated exposure before adding disruption",
        principle=(
            "If the same defensive problem is repeating, an intervention "
            "should aim to reduce the specific exposure while avoiding "
            "unnecessary disruption elsewhere."
        ),
        caveat=(
            "A structural change is not automatically preferable to an "
            "instructional or personnel adjustment."
        ),
        tags=[
            "profile:protect_lead",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="chase_game_001",
        title="Attacking commitment changes transition exposure",
        principle=(
            "Increasing attacking numbers or positioning can create more "
            "support around attacking areas while also increasing the "
            "importance of transition security behind the attack."
        ),
        caveat=(
            "This describes a tactical trade-off, not a prediction that "
            "either outcome will occur."
        ),
        tags=[
            "profile:chase_game",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="chase_game_002",
        title="Change the attacking picture deliberately",
        principle=(
            "When chance creation is inadequate, an intervention can alter "
            "support distances, personnel or structure rather than simply "
            "increasing attacking urgency without a defined tactical change."
        ),
        caveat=(
            "The most appropriate intervention depends on the actual cause "
            "of the attacking problem."
        ),
        tags=[
            "profile:chase_game",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="control_game_001",
        title="Central numerical support can change midfield access",
        principle=(
            "Additional central support can alter passing options, spacing "
            "and second-ball coverage when midfield control is the stated "
            "problem."
        ),
        caveat=(
            "Additional numbers alone do not guarantee better possession "
            "or control."
        ),
        tags=[
            "profile:control_game",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="control_game_002",
        title="Protect existing relationships during structural change",
        principle=(
            "A midfield structural adjustment should consider how the "
            "change affects width, pressing responsibilities and existing "
            "player relationships."
        ),
        caveat=(
            "The effect depends on how familiar the players are with the "
            "new responsibilities."
        ),
        tags=[
            "profile:control_game",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="balanced_001",
        title="Prefer proportionate intervention when evidence is limited",
        principle=(
            "When the game state is relatively balanced and there is no "
            "dominant tactical emergency, lower-disruption interventions "
            "can be compared against more structural alternatives."
        ),
        caveat=(
            "A larger intervention may still be appropriate when the coach "
            "has information not represented in the supplied scenario."
        ),
        tags=[
            "profile:balanced",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="wide_threat_001",
        title="Avoid repeated isolated wide defending",
        principle=(
            "When a wide defender is repeatedly exposed, possible responses "
            "include changing cover, pressure on the ball, nearby support, "
            "personnel or the wider team structure."
        ),
        caveat=(
            "The scenario must establish that the wide exposure is actually "
            "occurring before it is treated as an observed fact."
        ),
        tags=[
            "wide_threat",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="wide_threat_002",
        title="Consider the source of the overload",
        principle=(
            "A wide defensive problem can originate from more than the "
            "individual defender, including inadequate nearby support, "
            "uncontrolled overlaps or ineffective pressure before the ball "
            "reaches the flank."
        ),
        caveat=(
            "The available scenario may not contain enough information to "
            "identify the true source."
        ),
        tags=[
            "wide_threat",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="booked_defender_001",
        title="Booking changes the risk context of repeated duels",
        principle=(
            "A booked defender repeatedly placed in difficult defensive "
            "duels may require additional protection or a personnel decision "
            "to be considered."
        ),
        caveat=(
            "A booking alone does not establish that substitution is the "
            "correct action."
        ),
        tags=[
            "booked_defender",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="red_card_001",
        title="Numerical disadvantage changes structural priorities",
        principle=(
            "A red card can change spacing, coverage responsibilities and "
            "the feasibility of maintaining the previous team structure."
        ),
        caveat=(
            "The appropriate response depends on scoreline, remaining time, "
            "player roles and the coach's objective."
        ),
        tags=[
            "red_card",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="substitution_001",
        title="Substitution feasibility depends on role fit",
        principle=(
            "A personnel option should only be treated as practically "
            "available when an appropriate replacement role is actually "
            "available and ready to enter."
        ),
        caveat=(
            "The application does not currently know player fitness, form "
            "or detailed individual characteristics unless supplied."
        ),
        tags=[
            "substitutions_available",
        ],
    ),
    TacticalKnowledgeItem(
        knowledge_id="observation_001",
        title="Separate observation from inference",
        principle=(
            "Coach observations can support tactical reasoning, but the "
            "system should keep directly reported events separate from "
            "assumptions about their cause."
        ),
        caveat=(
            "The application cannot independently verify coach observations "
            "at this stage."
        ),
        tags=[
            "coach_observation_present",
        ],
    ),
)


WIDE_TERMS = (
    "wing",
    "winger",
    "wide",
    "flank",
    "overlap",
    "full-back",
    "left-back",
    "right-back",
)


DEFENSIVE_TERMS = (
    "centre-back",
    "center-back",
    "defender",
    "defensive",
    "left-back",
    "right-back",
    "full-back",
)


def _contains_any(
    text: str,
    terms: Iterable[str],
) -> bool:
    lowered = text.lower()

    return any(
        term in lowered
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
            " ".join(scenario.red_cards),
            " ".join(
                scenario.available_substitutions
            ),
        ]
    )


def _context_tags(
    scenario: ScenarioCreate,
    profile: ScenarioProfile,
) -> list[str]:
    tags = {
        f"profile:{profile}",
    }

    text = _scenario_text(
        scenario
    )

    if _contains_any(
        text,
        WIDE_TERMS,
    ):
        tags.add(
            "wide_threat"
        )

    booked_defender = any(
        _contains_any(
            card,
            DEFENSIVE_TERMS,
        )
        for card in scenario.yellow_cards
    )

    if booked_defender:
        tags.add(
            "booked_defender"
        )

    if scenario.red_cards:
        tags.add(
            "red_card"
        )

    if scenario.available_substitutions:
        tags.add(
            "substitutions_available"
        )

    if scenario.coach_observations:
        tags.add(
            "coach_observation_present"
        )

    return sorted(
        tags
    )


def retrieve_tactical_knowledge(
    scenario: ScenarioCreate,
    decision_brief: DecisionBrief,
    limit: int = 6,
) -> RetrievedTacticalKnowledge:
    if limit < 1:
        raise ValueError(
            "Knowledge retrieval limit must be at least 1."
        )

    profile = decision_brief.scenario_profile

    context_tags = _context_tags(
        scenario,
        profile,
    )

    tag_set = set(
        context_tags
    )

    ranked: list[
        tuple[int, str, TacticalKnowledgeItem]
    ] = []

    for item in KNOWLEDGE_BASE:
        matched_tags = (
            tag_set
            & set(item.tags)
        )

        if not matched_tags:
            continue

        profile_match = (
            f"profile:{profile}"
            in matched_tags
        )

        score = (
            len(matched_tags) * 10
            + (5 if profile_match else 0)
        )

        ranked.append(
            (
                score,
                item.knowledge_id,
                item,
            )
        )

    ranked.sort(
        key=lambda row: (
            -row[0],
            row[1],
        )
    )

    selected = [
        item
        for _, _, item
        in ranked[:limit]
    ]

    return RetrievedTacticalKnowledge(
        scenario_profile=profile,
        context_tags=context_tags,
        items=selected,
    )