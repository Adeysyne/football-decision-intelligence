from app.models.scenario import ScenarioCreate
from app.services.ai_reasoning import (
    prepare_reasoning_input,
)
from app.services.decision_engine import (
    build_decision_brief,
)
from app.services.knowledge_retrieval import (
    retrieve_tactical_knowledge,
)
from tests.test_decision_engine import (
    BASE_SCENARIO,
)


def _retrieve():
    scenario = ScenarioCreate(
        **BASE_SCENARIO
    )

    brief = build_decision_brief(
        scenario
    )

    return (
        scenario,
        brief,
        retrieve_tactical_knowledge(
            scenario=scenario,
            decision_brief=brief,
        ),
    )


def test_retrieval_preserves_scenario_profile():
    _, brief, knowledge = _retrieve()

    assert (
        knowledge.scenario_profile
        == brief.scenario_profile
    )

    assert (
        knowledge.scenario_profile
        == "protect_lead"
    )


def test_retrieval_detects_relevant_context():
    _, _, knowledge = _retrieve()

    assert (
        "wide_threat"
        in knowledge.context_tags
    )

    assert (
        "booked_defender"
        in knowledge.context_tags
    )

    assert (
        "substitutions_available"
        in knowledge.context_tags
    )

    assert (
        "coach_observation_present"
        in knowledge.context_tags
    )


def test_retrieved_items_are_deterministic_and_unique():
    scenario, brief, first = _retrieve()

    second = retrieve_tactical_knowledge(
        scenario=scenario,
        decision_brief=brief,
    )

    first_ids = [
        item.knowledge_id
        for item in first.items
    ]

    second_ids = [
        item.knowledge_id
        for item in second.items
    ]

    assert first_ids == second_ids

    assert (
        len(first_ids)
        == len(set(first_ids))
    )


def test_reasoning_payload_contains_tactical_knowledge():
    scenario = ScenarioCreate(
        **BASE_SCENARIO
    )

    payload = prepare_reasoning_input(
        scenario
    )

    assert (
        "tactical_knowledge"
        in payload
    )

    knowledge = payload[
        "tactical_knowledge"
    ]

    assert (
        knowledge[
            "scenario_profile"
        ]
        == "protect_lead"
    )

    assert knowledge[
        "items"
    ]


def test_knowledge_does_not_claim_probability():
    _, _, knowledge = _retrieve()

    text = knowledge.model_dump_json().lower()

    assert "%" not in text
    assert "success rate" not in text

    for item in knowledge.items:
        assert (
            item.evidence_type
            == "internal_tactical_principle"
        )