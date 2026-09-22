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


# ============================================================
# API
# ============================================================


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


# ============================================================
# SESSION HELPERS
# ============================================================


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


def comma_list(
    value: str,
) -> list[str]:
    return [
        item.strip()
        for item in value.split(",")
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
        f"— {option['weighted_score']}/5"
    )


# ============================================================
# VERIFIED AI
# ============================================================


def verification_failure_message(
    error_text: str,
) -> tuple[str, str]:
    lowered = error_text.lower()

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
                "The AI explanation did not pass the "
                "required verification checks, so it "
                "has not been shown as trusted advice. "
                "The deterministic tactical decision "
                "brief remains available and unchanged."
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
                "The scenario is too large for the AI "
                "explanation step. Shorten the free-text "
                "notes and retry. The deterministic "
                "decision brief remains available."
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


# ============================================================
# DISPLAY HELPERS
# ============================================================


def show_decision_brief(
    brief: dict,
) -> None:
    col_1, col_2, col_3 = st.columns(
        3
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

        heading = option_label(
            option
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

            score_columns = st.columns(
                4
            )

            for index, (
                name,
                score,
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

            left, right = st.columns(
                2
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
        "This system provides decision support. "
        "The coach remains responsible for the "
        "final tactical decision."
    )


def show_verified_ai(
    result: dict,
    brief: dict,
) -> None:
    verification = result[
        "verification"
    ]

    left, right = st.columns(
        2
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
        "This explanation passed the verification gate."
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
        item["option_id"]:
        item["label"]
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

    left, right = st.columns(
        2
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
        ]["items"]:
            st.write(
                f"• **{item['title']}** — "
                f"{item['principle']}"
            )

        st.markdown(
            "**Critic review**"
        )

        for index, review in enumerate(
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


# ============================================================
# HEADER
# ============================================================


st.title(
    "⚽ Football Decision Intelligence"
)

st.caption(
    "Structured tactical decision support for coaches. "
    "The coach remains the final decision-maker."
)


# ============================================================
# HEALTH CHECK
# ============================================================


try:
    api_request(
        "GET",
        "/health",
        access_code="",
    )

except RuntimeError as exc:
    st.error(
        str(exc)
    )

    st.info(
        "Start FastAPI first with:\n\n"
        "`python -m uvicorn app.main:app --reload`"
    )

    st.stop()


# ============================================================
# PRIVATE BETA ACCESS
# ============================================================


if not st.session_state.get(
    "beta_authenticated",
    False,
):
    st.subheader(
        "🔐 Private Beta Access"
    )

    st.write(
        "This preview is currently limited to "
        "invited coaches and pilot users."
    )

    with st.form(
        "beta_access_form"
    ):
        entered_code = st.text_input(
            "Access code",
            type="password",
            placeholder=(
                "Enter your private beta code"
            ),
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
                "Enter the private beta access code."
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
                    "The private beta access code "
                    "was not accepted."
                )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================


with st.sidebar:
    st.header(
        "System"
    )

    st.success(
        "API connected"
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


# ============================================================
# TEAMS
# ============================================================


try:
    teams = api_request(
        "GET",
        "/api/v1/teams",
    )

except RuntimeError as exc:
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
                    placeholder="4-2-3-1",
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
        "Create a team profile in the sidebar "
        "before entering a match scenario."
    )

    st.stop()


selected_team = team_lookup[
    selected_team_name
]


previous_team_id = (
    st.session_state.get(
        "active_team_id"
    )
)


if (
    previous_team_id
    and previous_team_id
    != selected_team[
        "team_id"
    ]
):
    reset_live_state()


st.session_state[
    "active_team_id"
] = selected_team[
    "team_id"
]


with st.sidebar:
    if st.session_state.get(
        "decision_result"
    ):
        if st.button(
            "Start new analysis",
            use_container_width=True,
        ):
            reset_live_state()
            st.rerun()


# ============================================================
# TABS
# ============================================================


live_tab, history_tab, pilot_tab = st.tabs(
    [
        "Live Decision",
        "Team History",
        "Pilot Feedback",
    ]
)


# ============================================================
# LIVE DECISION TAB
# ============================================================


with live_tab:
    left, right = st.columns(
        2
    )

    with left:
        st.subheader(
            selected_team[
                "team_name"
            ]
        )

        st.markdown(
            f"**Default formation:** "
            f"{selected_team['default_formation'] or 'Not set'}"
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

    st.divider()

    st.header(
        "1. Match Scenario"
    )

    with st.form(
        "scenario_form"
    ):
        col_1, col_2, col_3 = st.columns(
            3
        )

        minute = col_1.number_input(
            "Minute",
            min_value=0,
            max_value=130,
            value=68,
            step=1,
        )

        our_score = col_2.number_input(
            "Our score",
            min_value=0,
            max_value=30,
            value=1,
            step=1,
        )

        opponent_score = col_3.number_input(
            "Opponent score",
            min_value=0,
            max_value=30,
            value=0,
            step=1,
        )

        opponent_name = st.text_input(
            "Opponent",
            placeholder="Example United",
        )

        col_1, col_2 = st.columns(
            2
        )

        our_formation = col_1.text_input(
            "Our formation",
            value=(
                selected_team[
                    "default_formation"
                ]
                or "4-2-3-1"
            ),
        )

        opponent_formation = (
            col_2.text_input(
                "Opponent formation",
                value="4-3-3",
            )
        )

        tactical_problem = st.text_area(
            "What tactical problem are you seeing?",
            placeholder=(
                "Their right winger is repeatedly "
                "getting behind our left-back."
            ),
        )

        objective = st.text_area(
            "What is your objective?",
            placeholder=(
                "Protect the lead without completely "
                "losing our attacking threat."
            ),
        )

        coach_observations = st.text_area(
            "Coach observations",
            placeholder=(
                "Our left-back is already booked "
                "and their right-back is beginning "
                "to overlap."
            ),
        )

        yellow_cards = st.text_input(
            "Yellow-carded roles",
            placeholder=(
                "Left-back, Defensive midfielder"
            ),
        )

        red_cards = st.text_input(
            "Red-carded roles"
        )

        substitutions = st.text_input(
            "Available substitutions / roles",
            placeholder=(
                "Centre-back, Left-back, "
                "Defensive midfielder"
            ),
        )

        requested_option_count = st.slider(
            "Number of tactical alternatives",
            min_value=2,
            max_value=4,
            value=3,
        )

        analyse_clicked = (
            st.form_submit_button(
                "Analyse Scenario",
                type="primary",
                use_container_width=True,
            )
        )

    if analyse_clicked:
        if len(
            tactical_problem.strip()
        ) < 10:
            st.error(
                "Describe the tactical problem "
                "in a little more detail."
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
                scenario_result = api_request(
                    "POST",
                    "/api/v1/scenarios",
                    json=scenario_payload,
                )

                decision_result = api_request(
                    "POST",
                    (
                        "/api/v1/decisions/"
                        "scenarios/"
                        f"{scenario_result['scenario_id']}"
                        "/analyse"
                    ),
                )

                st.session_state[
                    "scenario_result"
                ] = scenario_result

                st.session_state[
                    "decision_result"
                ] = decision_result

                st.success(
                    "Scenario analysed successfully."
                )

            except RuntimeError as exc:
                st.error(
                    str(exc)
                )

    scenario_result = st.session_state.get(
        "scenario_result"
    )

    decision_result = st.session_state.get(
        "decision_result"
    )

    if decision_result:
        brief = decision_result[
            "decision_brief"
        ]

        st.divider()

        st.header(
            "2. Tactical Decision Brief"
        )

        show_decision_brief(
            brief
        )

        # ====================================================
        # VERIFIED AI
        # ====================================================

        st.divider()

        st.header(
            "3. Verified AI Explanation"
        )

        verified_result = st.session_state.get(
            "verified_result"
        )

        verified_error = st.session_state.get(
            "verified_error"
        )

        attempts = st.session_state.get(
            "verification_attempts",
            0,
        )

        if verified_result:
            show_verified_ai(
                verified_result,
                brief,
            )

            if attempts:
                st.caption(
                    "Verification attempts this "
                    f"session: {attempts}"
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
                    "has been exposed. You can still "
                    "use the deterministic tactical "
                    "brief and make the final coaching "
                    "decision."
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
                        "Verification attempts this "
                        f"session: {attempts}"
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
                    "Only an explanation that passes "
                    "verification will be displayed."
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

        # ====================================================
        # COACH DECISION
        # ====================================================

        st.divider()

        st.header(
            "4. Coach Decision"
        )

        selection_result = st.session_state.get(
            "selection_result"
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

            selected_id = selection_result[
                "selected_option_id"
            ]

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
                chosen = st.radio(
                    "Select the option you want to implement",
                    list(
                        choices
                    ),
                )

                rationale = st.text_area(
                    "Coach rationale",
                    placeholder=(
                        "Why are you choosing "
                        "this option?"
                    ),
                    max_chars=1500,
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
                    result = api_request(
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

                    st.session_state[
                        "selection_result"
                    ] = result

                    st.rerun()

                except RuntimeError as exc:
                    st.error(
                        str(exc)
                    )

        # ====================================================
        # OUTCOME
        # ====================================================

        selection_result = st.session_state.get(
            "selection_result"
        )

        if selection_result:
            st.divider()

            st.header(
                "5. Record Match Outcome"
            )

            outcome_result = st.session_state.get(
                "outcome_result"
            )

            if outcome_result:
                st.success(
                    "Outcome saved."
                )

                left, right = st.columns(
                    2
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

                with st.form(
                    "outcome_form"
                ):
                    left, right = st.columns(
                        2
                    )

                    final_our_score = left.number_input(
                        "Final our score",
                        min_value=0,
                        max_value=30,
                        value=int(
                            current_scenario[
                                "our_score"
                            ]
                        ),
                        step=1,
                    )

                    final_opponent_score = (
                        right.number_input(
                            "Final opponent score",
                            min_value=0,
                            max_value=30,
                            value=int(
                                current_scenario[
                                    "opponent_score"
                                ]
                            ),
                            step=1,
                        )
                    )

                    assessment_map = {
                        "Helped": "helped",
                        "Neutral": "neutral",
                        "Hurt": "hurt",
                        "Unclear": "unclear",
                    }

                    assessment = st.selectbox(
                        "Coach assessment of the intervention",
                        list(
                            assessment_map
                        ),
                    )

                    outcome_summary = st.text_area(
                        "Outcome summary",
                        placeholder=(
                            "Describe what happened "
                            "after the intervention "
                            "without assuming causation."
                        ),
                        max_chars=2000,
                    )

                    observed_effects = st.text_area(
                        "Observed effects",
                        placeholder=(
                            "One observation per line.\n"
                            "Example: Wide exposure reduced."
                        ),
                        max_chars=2000,
                    )

                    next_time_notes = st.text_area(
                        "Notes for next time",
                        max_chars=2000,
                    )

                    save_outcome = (
                        st.form_submit_button(
                            "Save Match Outcome",
                            type="primary",
                            use_container_width=True,
                        )
                    )

                if save_outcome:
                    if len(
                        outcome_summary.strip()
                    ) < 5:
                        st.error(
                            "Add a short outcome summary."
                        )

                    else:
                        try:
                            result = api_request(
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

                            st.session_state[
                                "outcome_result"
                            ] = result

                            st.rerun()

                        except RuntimeError as exc:
                            st.error(
                                str(exc)
                            )


# ============================================================
# TEAM HISTORY TAB
# ============================================================


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

        columns = st.columns(
            4
        )

        columns[0].metric(
            "Scenarios",
            history[
                "scenario_count"
            ],
        )

        columns[1].metric(
            "Decisions",
            history[
                "decision_count"
            ],
        )

        columns[2].metric(
            "Coach selections",
            history[
                "selection_count"
            ],
        )

        columns[3].metric(
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
                "Count only. This is not a "
                "recommendation to follow the "
                "engine leader."
            ),
        )

        left, right = st.columns(
            2
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


# ============================================================
# PILOT FEEDBACK TAB
# ============================================================


with pilot_tab:
    st.header(
        "Private Pilot Feedback"
    )

    st.write(
        "Your feedback helps us understand whether "
        "this tool is useful enough for real coaching "
        "workflows and what a practical pilot should "
        "look like."
    )

    st.caption(
        "The willingness-to-pay question is for "
        "product validation only. No payment is "
        "taken on this page."
    )

    existing_interest = st.session_state.get(
        "pilot_interest_result"
    )

    if existing_interest:
        st.success(
            "Thank you — your pilot feedback "
            "has been recorded."
        )

        left, right = st.columns(
            2
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
            coach_name = st.text_input(
                "Your name"
            )

            email = st.text_input(
                "Email"
            )

            club_or_team = st.text_input(
                "Club / team",
                value=(
                    selected_team[
                        "team_name"
                    ]
                ),
            )

            role = st.text_input(
                "Role",
                placeholder=(
                    "Head Coach, Assistant Coach, "
                    "Analyst..."
                ),
            )

            would_use = st.selectbox(
                "Would you use this in real match "
                "preparation or decision review?",
                list(
                    answer_map
                ),
            )

            join_pilot = st.selectbox(
                "Would you join a private pilot?",
                list(
                    answer_map
                ),
            )

            provide_value = st.checkbox(
                "I can give an indicative "
                "monthly value for this product."
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
                            "It is only product-validation data."
                        ),
                    )
                )

            most_valuable_feature = st.text_area(
                "Most valuable feature",
                placeholder=(
                    "Which part of the product "
                    "would matter most to you?"
                ),
                max_chars=1000,
            )

            pilot_feedback = st.text_area(
                "Feedback / feature request",
                placeholder=(
                    "What would need to improve "
                    "before you would use this regularly?"
                ),
                max_chars=3000,
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
                )
                < 5
                or "@"
                not in email
            ):
                st.error(
                    "Enter a valid email address."
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
                    result = api_request(
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

                    st.session_state[
                        "pilot_interest_result"
                    ] = result

                    st.rerun()

                except RuntimeError as exc:
                    st.error(
                        str(exc)
                    )