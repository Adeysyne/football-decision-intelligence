from app.models.ai_reasoning import AIReasoning
from app.services.ai_reasoning import (
    _humanise_option_references,
)


def test_machine_ids_are_hidden_from_coach_prose() -> None:
    decision_brief = {
        "options": [
            {
                "option_id": "option_1",
                "label": (
                    "Keep shape and add defensive support"
                ),
            },
            {
                "option_id": "option_2",
                "label": (
                    "Make a targeted defensive personnel change"
                ),
            },
            {
                "option_id": "option_3",
                "label": (
                    "Use a more conservative structure"
                ),
            },
        ]
    }

    reasoning = AIReasoning(
        summary=(
            "The engine ranks option_1 first, "
            "ahead of option_3 and option_2."
        ),
        option_explanations=[
            {
                "option_id": "option_1",
                "explanation": (
                    "option_1 preserves continuity."
                ),
                "main_risk": (
                    "option_1 may leave the threat."
                ),
                "assumption_to_check": (
                    "Confirm option_1 provides cover."
                ),
            },
            {
                "option_id": "option_2",
                "explanation": (
                    "option_2 changes personnel."
                ),
                "main_risk": (
                    "option_2 uses a substitution."
                ),
                "assumption_to_check": (
                    "Confirm option_2 has a replacement."
                ),
            },
            {
                "option_id": "option_3",
                "explanation": (
                    "option_3 adds defensive protection."
                ),
                "main_risk": (
                    "option_3 may reduce the outlet."
                ),
                "assumption_to_check": (
                    "Confirm option_3 can be executed."
                ),
            },
        ],
        missing_information=[
            "The effect of option_2 is unknown."
        ],
        questions_for_coach=[
            "Would option_3 leave the team too deep?"
        ],
    )

    polished = _humanise_option_references(
        reasoning,
        decision_brief,
    )

    # Internal identifiers must remain unchanged.
    assert [
        item.option_id
        for item in polished.option_explanations
    ] == [
        "option_1",
        "option_2",
        "option_3",
    ]

    prose = " ".join(
        [
            polished.summary,
            *[
                item.explanation
                for item
                in polished.option_explanations
            ],
            *[
                item.main_risk
                for item
                in polished.option_explanations
            ],
            *[
                item.assumption_to_check
                for item
                in polished.option_explanations
            ],
            *polished.missing_information,
            *polished.questions_for_coach,
        ]
    ).lower()

    assert "option_1" not in prose
    assert "option_2" not in prose
    assert "option_3" not in prose

    assert (
        "keep shape and add defensive support"
        in prose
    )

    assert (
        "make a targeted defensive personnel change"
        in prose
    )

    assert (
        "use a more conservative structure"
        in prose
    )
