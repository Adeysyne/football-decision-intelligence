import os

import httpx
import streamlit as st


API_BASE_URL = os.getenv(
    "FDI_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


st.set_page_config(
    page_title="Football Decision Intelligence",
    page_icon="⚽",
    layout="wide",
)


def api_request(
    method: str,
    path: str,
    timeout: float = 30.0,
    access_code: str | None = None,
    **kwargs,
):
    headers = dict(
        kwargs.pop(
            "headers",
            {},
        )
    )

    code = (
        access_code
        if access_code is not None
        else st.session_state.get(
            "beta_access_code",
            "",
        )
    )

    if code:
        headers[
            "X-Beta-Access-Code"
        ] = code

    try:
        response = httpx.request(
            method=method,
            url=f"{API_BASE_URL}{path}",
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Could not connect to the Football "
            "Decision Intelligence API."
        ) from exc

    if response.status_code >= 400:
        try:
            payload = response.json()

            detail = payload.get(
                "detail",
                response.text,
            )

            if isinstance(
                detail,
                dict,
            ):
                detail = detail.get(
                    "message",
                    str(detail),
                )

        except ValueError:
            detail = response.text

        raise RuntimeError(
            f"API error "
            f"({response.status_code}): "
            f"{detail}"
        )

    if not response.content:
        return None

    return response.json()


def reset_live_state() -> None:
    for key in (
        "scenario_result",
        "decision_result",
        "verified_result",
        "verified_error",
        "verification_attempts",
        "selection_result",
        "outcome_result",
    ):
        st.session_state.pop(
            key,
            None,
        )


def scenario_draft_key(
    team_id: str,
) -> str:
    return (
        f"scenario_draft::{team_id}"
    )


def default_scenario_draft(
    team: dict,
) -> dict:
    return {
        "minute": 68,
        "our_score": 1,
        "opponent_score": 0,
        "opponent_name": "",
        "our_formation": (
            team.get(
                "default_formation"
            )
            or "4-2-3-1"
        ),
        "opponent_formation": (
            "4-3-3"
        ),
        "tactical_problem": "",
        "objective": "",
        "coach_observations": "",
        "yellow_cards": "",
        "red_cards": "",
        "substitutions": "",
        "requested_option_count": 3,
    }


def draft_from_scenario(
    scenario: dict,
) -> dict:
    return {
        "minute": int(
            scenario.get(
                "minute",
                68,
            )
        ),
        "our_score": int(
            scenario.get(
                "our_score",
                1,
            )
        ),
        "opponent_score": int(
            scenario.get(
                "opponent_score",
                0,
            )
        ),
        "opponent_name": (
            scenario.get(
                "opponent_name"
            )
            or ""
        ),
        "our_formation": (
            scenario.get(
                "our_formation"
            )
            or "4-2-3-1"
        ),
        "opponent_formation": (
            scenario.get(
                "opponent_formation"
            )
            or ""
        ),
        "tactical_problem": (
            scenario.get(
                "tactical_problem"
            )
            or ""
        ),
        "objective": (
            scenario.get(
                "objective"
            )
            or ""
        ),
        "coach_observations": (
            scenario.get(
                "coach_observations"
            )
            or ""
        ),
        "yellow_cards": ", ".join(
            scenario.get(
                "yellow_cards",
                [],
            )
            or []
        ),
        "red_cards": ", ".join(
            scenario.get(
                "red_cards",
                [],
            )
            or []
        ),
        "substitutions": ", ".join(
            scenario.get(
                "available_substitutions",
                [],
            )
            or []
        ),
        "requested_option_count": int(
            scenario.get(
                "requested_option_count",
                3,
            )
        ),
    }


def get_scenario_draft(
    team: dict,
) -> dict:
    key = scenario_draft_key(
        str(
            team[
                "team_id"
            ]
        )
    )

    draft = st.session_state.get(
        key
    )

    if not isinstance(
        draft,
        dict,
    ):
        draft = (
            default_scenario_draft(
                team
            )
        )

        st.session_state[
            key
        ] = draft

    return draft


def save_scenario_draft(
    team_id: str,
    draft: dict,
) -> None:
    st.session_state[
        scenario_draft_key(
            team_id
        )
    ] = dict(
        draft
    )


def clear_scenario_draft(
    team: dict,
) -> None:
    st.session_state[
        scenario_draft_key(
            str(
                team[
                    "team_id"
                ]
            )
        )
    ] = default_scenario_draft(
        team
    )


def resume_checked_key(
    team_id: str,
) -> str:
    return (
        f"resume_checked::{team_id}"
    )


def resume_suppressed_key(
    team_id: str,
) -> str:
    return (
        f"resume_suppressed::{team_id}"
    )


def resume_notice_key(
    team_id: str,
) -> str:
    return (
        f"resume_notice::{team_id}"
    )


def scenario_widget_keys(
    team_id: str,
) -> list[str]:
    prefixes = [
        "scenario_minute",
        "scenario_our_score",
        "scenario_opponent_score",
        "scenario_opponent",
        "scenario_our_formation",
        "scenario_opponent_formation",
        "scenario_tactical_problem",
        "scenario_objective",
        "scenario_observations",
        "scenario_yellow_cards",
        "scenario_red_cards",
        "scenario_substitutions",
        "scenario_option_count",
    ]

    return [
        f"{prefix}::{team_id}"
        for prefix in prefixes
    ]


def clear_scenario_widget_state(
    team_id: str,
) -> None:
    for key in scenario_widget_keys(
        team_id
    ):
        st.session_state.pop(
            key,
            None,
        )


def apply_latest_workflow(
    team: dict,
    workflow: dict,
) -> None:
    team_id = str(
        team[
            "team_id"
        ]
    )

    scenario = (
        workflow.get(
            "scenario"
        )
        or {}
    )

    reset_live_state()

    save_scenario_draft(
        team_id,
        draft_from_scenario(
            scenario
        ),
    )

    clear_scenario_widget_state(
        team_id
    )

    st.session_state[
        "scenario_result"
    ] = {
        "scenario_id": workflow[
            "scenario_id"
        ],
        "status": "validated",
        "created_at": workflow[
            "scenario_created_at"
        ],
        "scenario": scenario,
        "next_step": (
            "decision_engine"
        ),
    }

    if (
        workflow.get(
            "decision_id"
        )
        and workflow.get(
            "decision_brief"
        )
    ):
        st.session_state[
            "decision_result"
        ] = {
            "decision_id": workflow[
                "decision_id"
            ],
            "scenario_id": workflow[
                "scenario_id"
            ],
            "created_at": (
                workflow.get(
                    "decision_created_at"
                )
            ),
            "decision_brief": workflow[
                "decision_brief"
            ],
        }

    if workflow.get(
        "selection"
    ):
        st.session_state[
            "selection_result"
        ] = workflow[
            "selection"
        ]

    if workflow.get(
        "outcome"
    ):
        st.session_state[
            "outcome_result"
        ] = workflow[
            "outcome"
        ]

    st.session_state[
        resume_notice_key(
            team_id
        )
    ] = True


def outcome_draft_key(
    decision_id: str,
) -> str:
    return (
        f"outcome_draft::{decision_id}"
    )


def get_outcome_draft(
    decision_id: str,
    scenario: dict,
) -> dict:
    key = outcome_draft_key(
        decision_id
    )

    draft = st.session_state.get(
        key
    )

    if not isinstance(
        draft,
        dict,
    ):
        draft = {
            "final_our_score": int(
                scenario.get(
                    "our_score",
                    0,
                )
            ),
            "final_opponent_score": int(
                scenario.get(
                    "opponent_score",
                    0,
                )
            ),
            "assessment": "Helped",
            "outcome_summary": "",
            "observed_effects": "",
            "next_time_notes": "",
        }

        st.session_state[
            key
        ] = draft

    return draft


def save_outcome_draft(
    decision_id: str,
    draft: dict,
) -> None:
    st.session_state[
        outcome_draft_key(
            decision_id
        )
    ] = dict(
        draft
    )


def comma_list(
    value: str,
) -> list[str]:
    return [
        item.strip()
        for item in value.split(
            ","
        )
        if item.strip()
    ]


def line_list(
    value: str,
) -> list[str]:
    return [
        item.strip()
        for item in value.splitlines()
        if item.strip()
    ]


def option_label(
    option: dict,
) -> str:
    return (
        f"{option['label']} "
        f"— "
        f"{option['weighted_score']}/5"
    )


def verification_failure_message(
    error_text: str,
) -> tuple[str, str]:
    lowered = (
        error_text.lower()
    )

    if (
        "could not be verified"
        in lowered
        or (
            "verification"
            in lowered
            and "502"
            in lowered
        )
    ):
        return (
            "Verification did not pass",
            (
                "The AI explanation did not pass "
                "the required verification checks, "
                "so it has not been shown as trusted "
                "advice. The deterministic tactical "
                "decision brief remains available "
                "and unchanged."
            ),
        )

    if (
        "503"
        in lowered
        or "provider unavailable"
        in lowered
    ):
        return (
            "AI service temporarily unavailable",
            (
                "The verified AI explanation service "
                "is temporarily unavailable. The "
                "deterministic tactical decision brief "
                "remains available, and you can retry "
                "the AI explanation later."
            ),
        )

    if (
        "413"
        in lowered
        or "shorten"
        in lowered
    ):
        return (
            "Scenario is too detailed",
            (
                "The scenario is too large for the "
                "AI explanation step. Shorten the "
                "free-text notes and retry. The "
                "deterministic decision brief remains "
                "available."
            ),
        )

    return (
        "Verified AI explanation unavailable",
        (
            "The verified explanation could not be "
            "completed. No unverified AI explanation "
            "has been displayed. The deterministic "
            "decision brief remains available."
        ),
    )


def run_verified_analysis(
    scenario: dict,
) -> None:
    attempts = (
        st.session_state.get(
            "verification_attempts",
            0,
        )
        + 1
    )

    st.session_state[
        "verification_attempts"
    ] = attempts

    try:
        with st.spinner(
            "Running grounded reasoning, "
            "critic review and verification..."
        ):
            result = api_request(
                "POST",
                "/api/v1/ai/analyse-verified",
                timeout=120.0,
                json=scenario,
            )

        st.session_state[
            "verified_result"
        ] = result

        st.session_state.pop(
            "verified_error",
            None,
        )

        st.rerun()

    except RuntimeError as exc:
        title, message = (
            verification_failure_message(
                str(exc)
            )
        )

        st.session_state[
            "verified_error"
        ] = {
            "title": title,
            "message": message,
            "technical_detail": str(
                exc
            ),
        }

        st.rerun()


def show_decision_brief(
    brief: dict,
) -> None:
    col_1, col_2, col_3 = (
        st.columns(
            3
        )
    )

    col_1.metric(
        "Scenario profile",
        brief[
            "scenario_profile"
        ].replace(
            "_",
            " ",
        ).title(),
    )

    col_2.metric(
        "Confidence",
        brief[
            "confidence"
        ].title(),
    )

    col_3.metric(
        "Options",
        len(
            brief[
                "options"
            ]
        ),
    )

    st.info(
        brief[
            "leading_option_reason"
        ]
    )

    st.caption(
        brief[
            "scoring_note"
        ]
    )

    st.subheader(
        "Tactical alternatives"
    )

    for option in brief[
        "options"
    ]:
        is_leader = (
            option[
                "option_id"
            ]
            == brief[
                "leading_option_id"
            ]
        )

        heading = (
            option_label(
                option
            )
        )

        if is_leader:
            heading += (
                " · Engine leading option"
            )

        with st.expander(
            heading,
            expanded=is_leader,
        ):
            st.write(
                option[
                    "description"
                ]
            )

            score_columns = (
                st.columns(
                    4
                )
            )

            for (
                index,
                (
                    name,
                    score,
                ),
            ) in enumerate(
                option[
                    "scores"
                ].items()
            ):
                score_columns[
                    index % 4
                ].metric(
                    name.replace(
                        "_",
                        " ",
                    ).title(),
                    f"{score}/5",
                )

            left, right = (
                st.columns(
                    2
                )
            )

            with left:
                st.markdown(
                    "**Strengths**"
                )

                for item in option[
                    "strengths"
                ]:
                    st.write(
                        f"• {item}"
                    )

            with right:
                st.markdown(
                    "**Risks**"
                )

                for item in option[
                    "risks"
                ]:
                    st.write(
                        f"• {item}"
                    )

            st.markdown(
                "**Assumptions**"
            )

            for item in option[
                "assumptions"
            ]:
                st.write(
                    f"• {item}"
                )

    st.subheader(
        "What to monitor next"
    )

    for item in brief[
        "monitor_next"
    ]:
        st.write(
            f"• {item}"
        )

    st.warning(
        "This system provides decision "
        "support. The coach remains "
        "responsible for the final "
        "tactical decision."
    )


def show_verified_ai(
    result: dict,
    brief: dict,
) -> None:
    verification = result[
        "verification"
    ]

    left, right = (
        st.columns(
            2
        )
    )

    left.metric(
        "Verification",
        verification[
            "status"
        ].title(),
    )

    right.metric(
        "Revision required",
        (
            "Yes"
            if verification[
                "revised"
            ]
            else "No"
        ),
    )

    st.success(
        "This explanation passed the "
        "verification gate."
    )

    reasoning = result[
        "ai_reasoning"
    ]

    st.markdown(
        "**AI summary**"
    )

    st.write(
        reasoning[
            "summary"
        ]
    )

    option_names = {
        item[
            "option_id"
        ]: item[
            "label"
        ]
        for item in brief[
            "options"
        ]
    }

    st.subheader(
        "Option explanations"
    )

    for item in reasoning[
        "option_explanations"
    ]:
        with st.expander(
            option_names.get(
                item[
                    "option_id"
                ],
                item[
                    "option_id"
                ],
            )
        ):
            st.write(
                item[
                    "explanation"
                ]
            )

            st.markdown(
                f"**Main risk:** "
                f"{item['main_risk']}"
            )

            st.markdown(
                f"**Assumption to check:** "
                f"{item['assumption_to_check']}"
            )

    left, right = (
        st.columns(
            2
        )
    )

    with left:
        st.markdown(
            "**Missing information**"
        )

        if reasoning[
            "missing_information"
        ]:
            for item in reasoning[
                "missing_information"
            ]:
                st.write(
                    f"• {item}"
                )

        else:
            st.write(
                "No additional missing "
                "information flagged."
            )

    with right:
        st.markdown(
            "**Questions for coach**"
        )

        if reasoning[
            "questions_for_coach"
        ]:
            for item in reasoning[
                "questions_for_coach"
            ]:
                st.write(
                    f"• {item}"
                )

        else:
            st.write(
                "No additional questions flagged."
            )

    with st.expander(
        "Grounding and verification details"
    ):
        st.markdown(
            "**Retrieved tactical principles**"
        )

        for item in result[
            "tactical_knowledge"
        ][
            "items"
        ]:
            st.write(
                f"• **{item['title']}** "
                f"— {item['principle']}"
            )

        st.markdown(
            "**Critic review**"
        )

        for (
            index,
            review,
        ) in enumerate(
            verification[
                "review_attempts"
            ],
            start=1,
        ):
            st.write(
                f"Review {index}: "
                f"{review['status'].replace('_', ' ').title()}"
            )

            st.caption(
                review[
                    "summary"
                ]
            )

            for issue in review[
                "issues"
            ]:
                st.write(
                    f"• {issue['problem']}"
                )


st.title(
    "⚽ Football Decision Intelligence"
)

st.caption(
    "Structured tactical decision support "
    "for coaches. The coach remains the "
    "final decision-maker."
)


api_connected = True


try:
    api_request(
        "GET",
        "/health",
        access_code="",
    )

except RuntimeError as exc:
    api_connected = False

    if st.session_state.get(
        "beta_authenticated",
        False,
    ):
        st.warning(
            "The API is temporarily unavailable. "
            "Your in-progress form data is being "
            "kept in this session while the "
            "connection recovers."
        )

    else:
        st.error(
            str(exc)
        )

        st.info(
            "The backend API must be "
            "available before private beta "
            "access can be verified."
        )

        st.stop()


if not st.session_state.get(
    "beta_authenticated",
    False,
):
    st.subheader(
        "🔐 Private Beta Access"
    )

    st.write(
        "This preview is currently limited "
        "to invited coaches and pilot users."
    )

    with st.form(
        "beta_access_form"
    ):
        entered_code = (
            st.text_input(
                "Access code",
                type="password",
                placeholder=(
                    "Enter your private beta code"
                ),
            )
        )

        unlock_clicked = (
            st.form_submit_button(
                "Enter Private Beta",
                type="primary",
                use_container_width=True,
            )
        )

    if unlock_clicked:
        if not entered_code.strip():
            st.error(
                "Enter the private beta "
                "access code."
            )

        else:
            try:
                api_request(
                    "GET",
                    "/api/v1/teams",
                    access_code=(
                        entered_code.strip()
                    ),
                )

                st.session_state[
                    "beta_access_code"
                ] = entered_code.strip()

                st.session_state[
                    "beta_authenticated"
                ] = True

                st.rerun()

            except RuntimeError:
                st.error(
                    "The private beta access "
                    "code was not accepted."
                )

    st.stop()


with st.sidebar:
    st.header(
        "System"
    )

    if api_connected:
        st.success(
            "API connected"
        )

    else:
        st.warning(
            "API reconnecting"
        )

    st.success(
        "Private beta unlocked"
    )

    if st.button(
        "Lock / Sign out",
        use_container_width=True,
    ):
        st.session_state.clear()
        st.rerun()


try:
    teams = api_request(
        "GET",
        "/api/v1/teams",
    )

    st.session_state[
        "teams_cache"
    ] = teams

    api_connected = True

except RuntimeError as exc:
    cached_teams = (
        st.session_state.get(
            "teams_cache"
        )
    )

    if cached_teams:
        teams = cached_teams
        api_connected = False

        st.warning(
            "The API connection dropped "
            "temporarily. Showing the last "
            "team data loaded in this browser "
            "session so your form is not lost."
        )

    else:
        st.error(
            str(exc)
        )

        st.stop()


with st.sidebar:
    st.header(
        "Team"
    )

    team_lookup = {
        team[
            "team_name"
        ]: team
        for team in teams
    }

    team_names = list(
        team_lookup
    )

    preferred = (
        st.session_state.pop(
            "preferred_team_name",
            None,
        )
    )

    selected_team_name = None

    if team_names:
        if (
            preferred
            in team_names
        ):
            selected_index = (
                team_names.index(
                    preferred
                )
            )

        else:
            selected_index = 0

        selected_team_name = (
            st.selectbox(
                "Current team",
                team_names,
                index=selected_index,
            )
        )

    else:
        st.info(
            "No team profile exists yet."
        )

    with st.expander(
        "Create new team"
    ):
        with st.form(
            "create_team_form"
        ):
            new_team_name = (
                st.text_input(
                    "Team name"
                )
            )

            new_formation = (
                st.text_input(
                    "Default formation",
                    value="4-2-3-1",
                    help=(
                        "This is saved as the team's "
                        "default formation and can "
                        "still be changed for an "
                        "individual scenario."
                    ),
                )
            )

            new_identity = (
                st.text_area(
                    "Tactical identity",
                    placeholder=(
                        "Compact defensive structure "
                        "with controlled transitions."
                    ),
                )
            )

            create_clicked = (
                st.form_submit_button(
                    "Create team",
                    type="primary",
                )
            )

        if create_clicked:
            if not new_team_name.strip():
                st.error(
                    "Enter a team name."
                )

            else:
                try:
                    created = api_request(
                        "POST",
                        "/api/v1/teams",
                        json={
                            "team_name": (
                                new_team_name.strip()
                            ),
                            "default_formation": (
                                new_formation.strip()
                                or None
                            ),
                            "tactical_identity": (
                                new_identity.strip()
                                or None
                            ),
                            "notes": None,
                        },
                    )

                    st.session_state[
                        "preferred_team_name"
                    ] = created[
                        "team_name"
                    ]

                    st.rerun()

                except RuntimeError as exc:
                    st.error(
                        str(exc)
                    )


if not teams:
    st.warning(
        "Create a team profile in the "
        "sidebar before entering a "
        "match scenario."
    )

    st.stop()


selected_team = team_lookup[
    selected_team_name
]


current_team_id = str(
    selected_team[
        "team_id"
    ]
)


previous_team_id = (
    st.session_state.get(
        "active_team_id"
    )
)


if (
    previous_team_id
    and str(
        previous_team_id
    )
    != current_team_id
):
    reset_live_state()

    st.session_state.pop(
        resume_checked_key(
            current_team_id
        ),
        None,
    )


st.session_state[
    "active_team_id"
] = current_team_id


if (
    not st.session_state.get(
        "decision_result"
    )
    and not st.session_state.get(
        resume_suppressed_key(
            current_team_id
        ),
        False,
    )
    and not st.session_state.get(
        resume_checked_key(
            current_team_id
        ),
        False,
    )
):
    try:
        latest_workflow = api_request(
            "GET",
            (
                "/api/v1/teams/"
                f"{current_team_id}"
                "/latest-workflow"
            ),
        )

        st.session_state[
            resume_checked_key(
                current_team_id
            )
        ] = True

        if (
            latest_workflow
            and not latest_workflow.get(
                "is_complete",
                False,
            )
        ):
            apply_latest_workflow(
                selected_team,
                latest_workflow,
            )

    except RuntimeError:
        pass


scenario_draft = (
    get_scenario_draft(
        selected_team
    )
)


with st.sidebar:
    if st.session_state.get(
        "decision_result"
    ):
        if st.button(
            "Start new analysis",
            use_container_width=True,
        ):
            reset_live_state()

            clear_scenario_draft(
                selected_team
            )

            clear_scenario_widget_state(
                current_team_id
            )

            st.session_state[
                resume_suppressed_key(
                    current_team_id
                )
            ] = True

            st.session_state[
                resume_notice_key(
                    current_team_id
                )
            ] = False

            st.rerun()

    elif st.session_state.get(
        resume_suppressed_key(
            current_team_id
        ),
        False,
    ):
        if st.button(
            "Resume latest saved analysis",
            use_container_width=True,
        ):
            st.session_state[
                resume_suppressed_key(
                    current_team_id
                )
            ] = False

            st.session_state[
                resume_checked_key(
                    current_team_id
                )
            ] = False

            st.rerun()


live_tab, history_tab, pilot_tab = (
    st.tabs(
        [
            "Live Decision",
            "Team History",
            "Pilot Feedback",
        ]
    )
)


with live_tab:
    left, right = (
        st.columns(
            2
        )
    )

    with left:
        st.subheader(
            selected_team[
                "team_name"
            ]
        )

        displayed_formation = (
            selected_team.get(
                "default_formation"
            )
            or scenario_draft.get(
                "our_formation"
            )
            or "Not set"
        )

        st.markdown(
            f"**Default formation:** "
            f"{displayed_formation}"
        )

    with right:
        st.markdown(
            "**Tactical identity:**"
        )

        st.write(
            selected_team[
                "tactical_identity"
            ]
            or "Not set"
        )

    if st.session_state.get(
        resume_notice_key(
            current_team_id
        ),
        False,
    ):
        st.success(
            "Resumed the latest unfinished "
            "analysis from the production "
            "database. The saved scenario "
            "and coach decision have been "
            "restored."
        )

        st.caption(
            "Verified AI is not rerun "
            "automatically. You can continue "
            "directly from the saved coach "
            "decision and record the match "
            "outcome."
        )

    st.divider()

    st.header(
        "1. Match Scenario"
    )

    if (
        not st.session_state.get(
            "scenario_result"
        )
        and any(
            [
                scenario_draft.get(
                    "opponent_name"
                ),
                scenario_draft.get(
                    "tactical_problem"
                ),
                scenario_draft.get(
                    "objective"
                ),
                scenario_draft.get(
                    "coach_observations"
                ),
                scenario_draft.get(
                    "yellow_cards"
                ),
                scenario_draft.get(
                    "substitutions"
                ),
            ]
        )
    ):
        st.info(
            "Recovered your in-progress "
            "scenario values from this "
            "browser session. Review them "
            "and click Analyse Scenario "
            "to continue."
        )

    team_widget_id = str(
        selected_team[
            "team_id"
        ]
    )

    with st.form(
        "scenario_form"
    ):
        col_1, col_2, col_3 = (
            st.columns(
                3
            )
        )

        minute = (
            col_1.number_input(
                "Minute",
                min_value=0,
                max_value=130,
                value=int(
                    scenario_draft.get(
                        "minute",
                        68,
                    )
                ),
                step=1,
                key=(
                    f"scenario_minute::"
                    f"{team_widget_id}"
                ),
            )
        )

        our_score = (
            col_2.number_input(
                "Our score",
                min_value=0,
                max_value=30,
                value=int(
                    scenario_draft.get(
                        "our_score",
                        1,
                    )
                ),
                step=1,
                key=(
                    f"scenario_our_score::"
                    f"{team_widget_id}"
                ),
            )
        )

        opponent_score = (
            col_3.number_input(
                "Opponent score",
                min_value=0,
                max_value=30,
                value=int(
                    scenario_draft.get(
                        "opponent_score",
                        0,
                    )
                ),
                step=1,
                key=(
                    f"scenario_opponent_score::"
                    f"{team_widget_id}"
                ),
            )
        )

        opponent_name = (
            st.text_input(
                "Opponent",
                value=(
                    scenario_draft.get(
                        "opponent_name",
                        "",
                    )
                ),
                placeholder=(
                    "Example United"
                ),
                key=(
                    f"scenario_opponent::"
                    f"{team_widget_id}"
                ),
            )
        )

        col_1, col_2 = (
            st.columns(
                2
            )
        )

        our_formation = (
            col_1.text_input(
                "Our formation",
                value=(
                    scenario_draft.get(
                        "our_formation"
                    )
                    or selected_team.get(
                        "default_formation"
                    )
                    or "4-2-3-1"
                ),
                key=(
                    f"scenario_our_formation::"
                    f"{team_widget_id}"
                ),
            )
        )

        opponent_formation = (
            col_2.text_input(
                "Opponent formation",
                value=(
                    scenario_draft.get(
                        "opponent_formation"
                    )
                    or "4-3-3"
                ),
                key=(
                    f"scenario_opponent_formation::"
                    f"{team_widget_id}"
                ),
            )
        )

        tactical_problem = (
            st.text_area(
                "What tactical problem "
                "are you seeing?",
                value=(
                    scenario_draft.get(
                        "tactical_problem",
                        "",
                    )
                ),
                placeholder=(
                    "Their right winger is "
                    "repeatedly getting behind "
                    "our left-back."
                ),
                key=(
                    f"scenario_tactical_problem::"
                    f"{team_widget_id}"
                ),
            )
        )

        objective = (
            st.text_area(
                "What is your objective?",
                value=(
                    scenario_draft.get(
                        "objective",
                        "",
                    )
                ),
                placeholder=(
                    "Protect the lead without "
                    "completely losing our "
                    "attacking threat."
                ),
                key=(
                    f"scenario_objective::"
                    f"{team_widget_id}"
                ),
            )
        )

        coach_observations = (
            st.text_area(
                "Coach observations",
                value=(
                    scenario_draft.get(
                        "coach_observations",
                        "",
                    )
                ),
                placeholder=(
                    "Our left-back is already "
                    "booked and their right-back "
                    "is beginning to overlap."
                ),
                key=(
                    f"scenario_observations::"
                    f"{team_widget_id}"
                ),
            )
        )

        yellow_cards = (
            st.text_input(
                "Yellow-carded roles",
                value=(
                    scenario_draft.get(
                        "yellow_cards",
                        "",
                    )
                ),
                placeholder=(
                    "Left-back, "
                    "Defensive midfielder"
                ),
                key=(
                    f"scenario_yellow_cards::"
                    f"{team_widget_id}"
                ),
            )
        )

        red_cards = (
            st.text_input(
                "Red-carded roles",
                value=(
                    scenario_draft.get(
                        "red_cards",
                        "",
                    )
                ),
                key=(
                    f"scenario_red_cards::"
                    f"{team_widget_id}"
                ),
            )
        )

        substitutions = (
            st.text_input(
                "Available substitutions / roles",
                value=(
                    scenario_draft.get(
                        "substitutions",
                        "",
                    )
                ),
                placeholder=(
                    "Centre-back, Left-back, "
                    "Defensive midfielder"
                ),
                key=(
                    f"scenario_substitutions::"
                    f"{team_widget_id}"
                ),
            )
        )

        requested_option_count = (
            st.slider(
                "Number of tactical alternatives",
                min_value=2,
                max_value=4,
                value=int(
                    scenario_draft.get(
                        "requested_option_count",
                        3,
                    )
                ),
                key=(
                    f"scenario_option_count::"
                    f"{team_widget_id}"
                ),
            )
        )

        analyse_clicked = (
            st.form_submit_button(
                "Analyse Scenario",
                type="primary",
                use_container_width=True,
            )
        )

    if analyse_clicked:
        submitted_draft = {
            "minute": int(
                minute
            ),
            "our_score": int(
                our_score
            ),
            "opponent_score": int(
                opponent_score
            ),
            "opponent_name": (
                opponent_name.strip()
            ),
            "our_formation": (
                our_formation.strip()
            ),
            "opponent_formation": (
                opponent_formation.strip()
            ),
            "tactical_problem": (
                tactical_problem.strip()
            ),
            "objective": (
                objective.strip()
            ),
            "coach_observations": (
                coach_observations.strip()
            ),
            "yellow_cards": (
                yellow_cards.strip()
            ),
            "red_cards": (
                red_cards.strip()
            ),
            "substitutions": (
                substitutions.strip()
            ),
            "requested_option_count": int(
                requested_option_count
            ),
        }

        save_scenario_draft(
            str(
                selected_team[
                    "team_id"
                ]
            ),
            submitted_draft,
        )

        scenario_draft = (
            submitted_draft
        )

        if len(
            tactical_problem.strip()
        ) < 10:
            st.error(
                "Describe the tactical "
                "problem in a little more "
                "detail."
            )

        elif len(
            objective.strip()
        ) < 5:
            st.error(
                "Enter the tactical objective."
            )

        else:
            reset_live_state()

            scenario_payload = {
                "team_name": (
                    selected_team[
                        "team_name"
                    ]
                ),
                "opponent_name": (
                    opponent_name.strip()
                    or None
                ),
                "minute": int(
                    minute
                ),
                "our_score": int(
                    our_score
                ),
                "opponent_score": int(
                    opponent_score
                ),
                "our_formation": (
                    our_formation.strip()
                ),
                "opponent_formation": (
                    opponent_formation.strip()
                    or None
                ),
                "yellow_cards": (
                    comma_list(
                        yellow_cards
                    )
                ),
                "red_cards": (
                    comma_list(
                        red_cards
                    )
                ),
                "available_substitutions": (
                    comma_list(
                        substitutions
                    )
                ),
                "tactical_problem": (
                    tactical_problem.strip()
                ),
                "objective": (
                    objective.strip()
                ),
                "coach_observations": (
                    coach_observations.strip()
                    or None
                ),
                "options": [],
                "requested_option_count": (
                    requested_option_count
                ),
            }

            try:
                scenario_result = (
                    api_request(
                        "POST",
                        "/api/v1/scenarios",
                        json=scenario_payload,
                    )
                )

                decision_result = (
                    api_request(
                        "POST",
                        (
                            "/api/v1/decisions/"
                            "scenarios/"
                            f"{scenario_result['scenario_id']}"
                            "/analyse"
                        ),
                    )
                )

                st.session_state[
                    "scenario_result"
                ] = scenario_result

                st.session_state[
                    "decision_result"
                ] = decision_result

                save_scenario_draft(
                    str(
                        selected_team[
                            "team_id"
                        ]
                    ),
                    draft_from_scenario(
                        scenario_result[
                            "scenario"
                        ]
                    ),
                )

                st.session_state[
                    resume_suppressed_key(
                        current_team_id
                    )
                ] = False

                st.session_state[
                    resume_checked_key(
                        current_team_id
                    )
                ] = True

                st.session_state[
                    resume_notice_key(
                        current_team_id
                    )
                ] = False

                st.success(
                    "Scenario analysed "
                    "successfully."
                )

            except RuntimeError as exc:
                st.error(
                    str(exc)
                )

    scenario_result = (
        st.session_state.get(
            "scenario_result"
        )
    )

    decision_result = (
        st.session_state.get(
            "decision_result"
        )
    )

    if decision_result:
        brief = (
            decision_result[
                "decision_brief"
            ]
        )

        st.divider()

        st.header(
            "2. Tactical Decision Brief"
        )

        show_decision_brief(
            brief
        )

        st.divider()

        st.header(
            "3. Verified AI Explanation"
        )

        verified_result = (
            st.session_state.get(
                "verified_result"
            )
        )

        verified_error = (
            st.session_state.get(
                "verified_error"
            )
        )

        attempts = (
            st.session_state.get(
                "verification_attempts",
                0,
            )
        )

        if verified_result:
            show_verified_ai(
                verified_result,
                brief,
            )

            if attempts:
                st.caption(
                    "Verification attempts "
                    f"this session: {attempts}"
                )

        else:
            if verified_error:
                st.warning(
                    f"**{verified_error['title']}**"
                )

                st.write(
                    verified_error[
                        "message"
                    ]
                )

                st.info(
                    "No unverified AI explanation "
                    "has been exposed. You can "
                    "still use the deterministic "
                    "tactical brief and make the "
                    "final coaching decision."
                )

                with st.expander(
                    "Technical detail"
                ):
                    st.code(
                        verified_error[
                            "technical_detail"
                        ]
                    )

                if attempts:
                    st.caption(
                        "Verification attempts "
                        f"this session: {attempts}"
                    )

                button_label = (
                    "Retry Verified AI Explanation"
                )

            else:
                st.write(
                    "Generate a grounded explanation "
                    "and pass it through the critic / "
                    "verification pipeline."
                )

                st.caption(
                    "Only an explanation that "
                    "passes verification will "
                    "be displayed."
                )

                button_label = (
                    "Run Verified AI Explanation"
                )

            if st.button(
                button_label,
                type="primary",
                use_container_width=True,
            ):
                run_verified_analysis(
                    scenario_result[
                        "scenario"
                    ]
                )

        st.divider()

        st.header(
            "4. Coach Decision"
        )

        selection_result = (
            st.session_state.get(
                "selection_result"
            )
        )

        options = brief[
            "options"
        ]

        if selection_result:
            option_names = {
                item[
                    "option_id"
                ]: item[
                    "label"
                ]
                for item in options
            }

            st.success(
                "Coach selection saved."
            )

            selected_id = (
                selection_result[
                    "selected_option_id"
                ]
            )

            st.markdown(
                f"**Selected option:** "
                f"{option_names.get(selected_id, selected_id)}"
            )

            if selection_result[
                "rationale"
            ]:
                st.markdown(
                    f"**Rationale:** "
                    f"{selection_result['rationale']}"
                )

        else:
            choices = {
                option_label(
                    item
                ): item[
                    "option_id"
                ]
                for item in options
            }

            with st.form(
                "coach_selection_form"
            ):
                chosen = (
                    st.radio(
                        "Select the option "
                        "you want to implement",
                        list(
                            choices
                        ),
                    )
                )

                rationale = (
                    st.text_area(
                        "Coach rationale",
                        placeholder=(
                            "Why are you choosing "
                            "this option?"
                        ),
                        max_chars=1500,
                    )
                )

                save_selection = (
                    st.form_submit_button(
                        "Save Coach Decision",
                        type="primary",
                        use_container_width=True,
                    )
                )

            if save_selection:
                try:
                    result = (
                        api_request(
                            "POST",
                            (
                                "/api/v1/decisions/"
                                f"{decision_result['decision_id']}"
                                "/selection"
                            ),
                            json={
                                "selected_option_id": (
                                    choices[
                                        chosen
                                    ]
                                ),
                                "rationale": (
                                    rationale.strip()
                                    or None
                                ),
                            },
                        )
                    )

                    st.session_state[
                        "selection_result"
                    ] = result

                    st.rerun()

                except RuntimeError as exc:
                    st.error(
                        str(exc)
                    )

        selection_result = (
            st.session_state.get(
                "selection_result"
            )
        )

        if selection_result:
            st.divider()

            st.header(
                "5. Record Match Outcome"
            )

            outcome_result = (
                st.session_state.get(
                    "outcome_result"
                )
            )

            if outcome_result:
                st.success(
                    "Outcome saved."
                )

                left, right = (
                    st.columns(
                        2
                    )
                )

                left.metric(
                    "Final score",
                    (
                        f"{outcome_result['final_our_score']}"
                        f"–"
                        f"{outcome_result['final_opponent_score']}"
                    ),
                )

                right.metric(
                    "Coach assessment",
                    outcome_result[
                        "coach_assessment"
                    ].title(),
                )

                st.markdown(
                    f"**Outcome summary:** "
                    f"{outcome_result['outcome_summary']}"
                )

                if outcome_result[
                    "observed_effects"
                ]:
                    st.markdown(
                        "**Observed effects:**"
                    )

                    for item in outcome_result[
                        "observed_effects"
                    ]:
                        st.write(
                            f"• {item}"
                        )

                if outcome_result[
                    "next_time_notes"
                ]:
                    st.markdown(
                        f"**Next-time notes:** "
                        f"{outcome_result['next_time_notes']}"
                    )

            else:
                current_scenario = (
                    scenario_result[
                        "scenario"
                    ]
                )

                decision_id = str(
                    decision_result[
                        "decision_id"
                    ]
                )

                outcome_draft = (
                    get_outcome_draft(
                        decision_id,
                        current_scenario,
                    )
                )

                assessment_map = {
                    "Helped": "helped",
                    "Neutral": "neutral",
                    "Hurt": "hurt",
                    "Unclear": "unclear",
                }

                assessment_labels = (
                    list(
                        assessment_map
                    )
                )

                saved_assessment = (
                    outcome_draft.get(
                        "assessment",
                        "Helped",
                    )
                )

                assessment_index = (
                    assessment_labels.index(
                        saved_assessment
                    )
                    if saved_assessment
                    in assessment_labels
                    else 0
                )

                with st.form(
                    "outcome_form"
                ):
                    left, right = (
                        st.columns(
                            2
                        )
                    )

                    final_our_score = (
                        left.number_input(
                            "Final our score",
                            min_value=0,
                            max_value=30,
                            value=int(
                                outcome_draft.get(
                                    "final_our_score",
                                    current_scenario[
                                        "our_score"
                                    ],
                                )
                            ),
                            step=1,
                            key=(
                                f"outcome_our_score::"
                                f"{decision_id}"
                            ),
                        )
                    )

                    final_opponent_score = (
                        right.number_input(
                            "Final opponent score",
                            min_value=0,
                            max_value=30,
                            value=int(
                                outcome_draft.get(
                                    "final_opponent_score",
                                    current_scenario[
                                        "opponent_score"
                                    ],
                                )
                            ),
                            step=1,
                            key=(
                                f"outcome_opponent_score::"
                                f"{decision_id}"
                            ),
                        )
                    )

                    assessment = (
                        st.selectbox(
                            "Coach assessment of "
                            "the intervention",
                            assessment_labels,
                            index=(
                                assessment_index
                            ),
                            key=(
                                f"outcome_assessment::"
                                f"{decision_id}"
                            ),
                        )
                    )

                    outcome_summary = (
                        st.text_area(
                            "Outcome summary",
                            value=(
                                outcome_draft.get(
                                    "outcome_summary",
                                    "",
                                )
                            ),
                            placeholder=(
                                "Describe what happened "
                                "after the intervention "
                                "without assuming causation."
                            ),
                            max_chars=2000,
                            key=(
                                f"outcome_summary::"
                                f"{decision_id}"
                            ),
                        )
                    )

                    observed_effects = (
                        st.text_area(
                            "Observed effects",
                            value=(
                                outcome_draft.get(
                                    "observed_effects",
                                    "",
                                )
                            ),
                            placeholder=(
                                "One observation per line.\n"
                                "Example: Wide exposure reduced."
                            ),
                            max_chars=2000,
                            key=(
                                f"outcome_effects::"
                                f"{decision_id}"
                            ),
                        )
                    )

                    next_time_notes = (
                        st.text_area(
                            "Notes for next time",
                            value=(
                                outcome_draft.get(
                                    "next_time_notes",
                                    "",
                                )
                            ),
                            max_chars=2000,
                            key=(
                                f"outcome_notes::"
                                f"{decision_id}"
                            ),
                        )
                    )

                    save_outcome = (
                        st.form_submit_button(
                            "Save Match Outcome",
                            type="primary",
                            use_container_width=True,
                        )
                    )

                if save_outcome:
                    submitted_outcome_draft = {
                        "final_our_score": int(
                            final_our_score
                        ),
                        "final_opponent_score": int(
                            final_opponent_score
                        ),
                        "assessment": (
                            assessment
                        ),
                        "outcome_summary": (
                            outcome_summary.strip()
                        ),
                        "observed_effects": (
                            observed_effects.strip()
                        ),
                        "next_time_notes": (
                            next_time_notes.strip()
                        ),
                    }

                    save_outcome_draft(
                        decision_id,
                        submitted_outcome_draft,
                    )

                    if len(
                        outcome_summary.strip()
                    ) < 5:
                        st.error(
                            "Add a short outcome summary."
                        )

                    else:
                        try:
                            result = (
                                api_request(
                                    "POST",
                                    (
                                        "/api/v1/decisions/"
                                        f"{decision_result['decision_id']}"
                                        "/outcome"
                                    ),
                                    json={
                                        "final_our_score": int(
                                            final_our_score
                                        ),
                                        "final_opponent_score": int(
                                            final_opponent_score
                                        ),
                                        "coach_assessment": (
                                            assessment_map[
                                                assessment
                                            ]
                                        ),
                                        "outcome_summary": (
                                            outcome_summary.strip()
                                        ),
                                        "observed_effects": (
                                            line_list(
                                                observed_effects
                                            )
                                        ),
                                        "next_time_notes": (
                                            next_time_notes.strip()
                                            or None
                                        ),
                                    },
                                )
                            )

                            st.session_state[
                                "outcome_result"
                            ] = result

                            st.rerun()

                        except RuntimeError as exc:
                            st.error(
                                str(exc)
                            )

                            st.info(
                                "Your outcome form values "
                                "have been kept in this "
                                "browser session. Once the "
                                "API reconnects, return here "
                                "and submit again without "
                                "retyping them."
                            )


with history_tab:
    st.header(
        f"{selected_team['team_name']} "
        "— Team History"
    )

    st.caption(
        "Historical counts are descriptive. "
        "Coach assessments do not establish "
        "that a tactical intervention caused "
        "a match outcome."
    )

    try:
        history = api_request(
            "GET",
            (
                "/api/v1/teams/"
                f"{selected_team['team_id']}"
                "/history-summary"
            ),
        )

        columns = (
            st.columns(
                4
            )
        )

        columns[
            0
        ].metric(
            "Scenarios",
            history[
                "scenario_count"
            ],
        )

        columns[
            1
        ].metric(
            "Decisions",
            history[
                "decision_count"
            ],
        )

        columns[
            2
        ].metric(
            "Coach selections",
            history[
                "selection_count"
            ],
        )

        columns[
            3
        ].metric(
            "Recorded outcomes",
            history[
                "outcome_count"
            ],
        )

        st.subheader(
            "Decision behaviour"
        )

        st.metric(
            "Engine-leading option selected",
            history[
                "engine_leader_selected_count"
            ],
            help=(
                "Count only. This is not "
                "a recommendation to follow "
                "the engine leader."
            ),
        )

        left, right = (
            st.columns(
                2
            )
        )

        with left:
            st.markdown(
                "**Coach outcome assessments**"
            )

            for (
                name,
                count,
            ) in history[
                "assessment_counts"
            ].items():
                st.write(
                    f"• {name.title()}: "
                    f"{count}"
                )

        with right:
            st.markdown(
                "**Scenario profiles**"
            )

            for (
                name,
                count,
            ) in history[
                "scenario_profile_counts"
            ].items():
                st.write(
                    f"• "
                    f"{name.replace('_', ' ').title()}: "
                    f"{count}"
                )

        st.info(
            history[
                "data_note"
            ]
        )

        if st.button(
            "Refresh Team History",
            use_container_width=True,
        ):
            st.rerun()

    except RuntimeError as exc:
        st.error(
            str(exc)
        )


with pilot_tab:
    st.header(
        "Private Pilot Feedback"
    )

    st.write(
        "Your feedback helps us understand "
        "whether this tool is useful enough "
        "for real coaching workflows and "
        "what a practical pilot should "
        "look like."
    )

    st.caption(
        "The willingness-to-pay question "
        "is for product validation only. "
        "No payment is taken on this page."
    )

    existing_interest = (
        st.session_state.get(
            "pilot_interest_result"
        )
    )

    if existing_interest:
        st.success(
            "Thank you — your pilot "
            "feedback has been recorded."
        )

        left, right = (
            st.columns(
                2
            )
        )

        pilot_answer = (
            existing_interest[
                "join_private_pilot"
            ].title()
        )

        left.markdown(
            f"**Pilot interest:** "
            f"{pilot_answer}"
        )

        monthly_value = (
            existing_interest[
                "willingness_to_pay_monthly_gbp"
            ]
        )

        if monthly_value is not None:
            monthly_text = (
                f"£{monthly_value}"
            )

        else:
            monthly_text = (
                "Not specified"
            )

        right.markdown(
            f"**Indicative monthly value:** "
            f"{monthly_text}"
        )

    else:
        answer_map = {
            "Yes": "yes",
            "Maybe": "maybe",
            "No": "no",
        }

        with st.form(
            "pilot_interest_form"
        ):
            coach_name = (
                st.text_input(
                    "Your name"
                )
            )

            email = (
                st.text_input(
                    "Email"
                )
            )

            club_or_team = (
                st.text_input(
                    "Club / team",
                    value=(
                        selected_team[
                            "team_name"
                        ]
                    ),
                )
            )

            role = (
                st.text_input(
                    "Role",
                    placeholder=(
                        "Head Coach, "
                        "Assistant Coach, "
                        "Analyst..."
                    ),
                )
            )

            would_use = (
                st.selectbox(
                    "Would you use this "
                    "in real match preparation "
                    "or decision review?",
                    list(
                        answer_map
                    ),
                )
            )

            join_pilot = (
                st.selectbox(
                    "Would you join a "
                    "private pilot?",
                    list(
                        answer_map
                    ),
                )
            )

            provide_value = (
                st.checkbox(
                    "I can give an indicative "
                    "monthly value for this "
                    "product."
                )
            )

            willingness_to_pay = None

            if provide_value:
                willingness_to_pay = (
                    st.number_input(
                        "Indicative monthly value (£)",
                        min_value=0,
                        max_value=10000,
                        value=25,
                        step=5,
                        help=(
                            "This is not a payment. "
                            "It is only product-"
                            "validation data."
                        ),
                    )
                )

            most_valuable_feature = (
                st.text_area(
                    "Most valuable feature",
                    placeholder=(
                        "Which part of the "
                        "product would matter "
                        "most to you?"
                    ),
                    max_chars=1000,
                )
            )

            pilot_feedback = (
                st.text_area(
                    "Feedback / feature request",
                    placeholder=(
                        "What would need to "
                        "improve before you "
                        "would use this regularly?"
                    ),
                    max_chars=3000,
                )
            )

            submit_interest = (
                st.form_submit_button(
                    "Submit Pilot Feedback",
                    type="primary",
                    use_container_width=True,
                )
            )

        if submit_interest:
            if len(
                coach_name.strip()
            ) < 2:
                st.error(
                    "Enter your name."
                )

            elif (
                len(
                    email.strip()
                ) < 5
                or "@"
                not in email
            ):
                st.error(
                    "Enter a valid email "
                    "address."
                )

            elif len(
                club_or_team.strip()
            ) < 2:
                st.error(
                    "Enter your club or team."
                )

            elif len(
                role.strip()
            ) < 2:
                st.error(
                    "Enter your role."
                )

            else:
                try:
                    result = (
                        api_request(
                            "POST",
                            "/api/v1/pilot-interest",
                            json={
                                "coach_name": (
                                    coach_name.strip()
                                ),
                                "email": (
                                    email.strip()
                                ),
                                "club_or_team": (
                                    club_or_team.strip()
                                ),
                                "role": (
                                    role.strip()
                                ),
                                "would_use_in_real_matches": (
                                    answer_map[
                                        would_use
                                    ]
                                ),
                                "join_private_pilot": (
                                    answer_map[
                                        join_pilot
                                    ]
                                ),
                                "willingness_to_pay_monthly_gbp": (
                                    int(
                                        willingness_to_pay
                                    )
                                    if provide_value
                                    else None
                                ),
                                "most_valuable_feature": (
                                    most_valuable_feature.strip()
                                    or None
                                ),
                                "feedback": (
                                    pilot_feedback.strip()
                                    or None
                                ),
                            },
                        )
                    )

                    st.session_state[
                        "pilot_interest_result"
                    ] = result

                    st.rerun()

                except RuntimeError as exc:
                    st.error(
                        str(exc)
                    )