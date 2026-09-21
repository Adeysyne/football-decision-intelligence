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
    **kwargs,
):
    url = (
        f"{API_BASE_URL}{path}"
    )

    try:
        response = httpx.request(
            method=method,
            url=url,
            timeout=30.0,
            **kwargs,
        )

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Could not connect to the Football "
            "Decision Intelligence API."
        ) from exc

    if response.status_code >= 400:
        try:
            detail = response.json().get(
                "detail",
                response.text,
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


def load_teams() -> list[dict]:
    return api_request(
        "GET",
        "/api/v1/teams",
    )


def reset_analysis() -> None:
    st.session_state.pop(
        "scenario_result",
        None,
    )

    st.session_state.pop(
        "decision_result",
        None,
    )

    st.session_state.pop(
        "selection_result",
        None,
    )


def option_score_label(
    option: dict,
) -> str:
    return (
        f"{option['label']} "
        f"— {option['weighted_score']}/5"
    )


st.title(
    "⚽ Football Decision Intelligence"
)

st.caption(
    "Structured tactical decision support for coaches. "
    "The coach remains the final decision-maker."
)


# -------------------------------------------------
# API STATUS
# -------------------------------------------------

with st.sidebar:
    st.header(
        "System"
    )

    try:
        health = api_request(
            "GET",
            "/health",
        )

        if (
            health.get("status")
            == "healthy"
        ):
            st.success(
                "API connected"
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


# -------------------------------------------------
# TEAM SELECTION / CREATION
# -------------------------------------------------

try:
    teams = load_teams()

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
        team["team_name"]: team
        for team in teams
    }

    team_names = list(
        team_lookup
    )

    selected_team_name = None

    if team_names:
        selected_team_name = (
            st.selectbox(
                "Current team",
                options=team_names,
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
            new_team_name = st.text_input(
                "Team name"
            )

            new_default_formation = (
                st.text_input(
                    "Default formation",
                    placeholder="4-2-3-1",
                )
            )

            new_tactical_identity = (
                st.text_area(
                    "Tactical identity",
                    placeholder=(
                        "Example: Compact defensive "
                        "shape with controlled transitions."
                    ),
                )
            )

            create_team_clicked = (
                st.form_submit_button(
                    "Create team",
                    type="primary",
                )
            )

        if create_team_clicked:
            if not new_team_name.strip():
                st.error(
                    "Enter a team name."
                )

            else:
                payload = {
                    "team_name": (
                        new_team_name.strip()
                    ),
                    "default_formation": (
                        new_default_formation.strip()
                        or None
                    ),
                    "tactical_identity": (
                        new_tactical_identity.strip()
                        or None
                    ),
                    "notes": None,
                }

                try:
                    created_team = (
                        api_request(
                            "POST",
                            "/api/v1/teams",
                            json=payload,
                        )
                    )

                    st.success(
                        "Team created."
                    )

                    st.session_state[
                        "preferred_team_name"
                    ] = created_team[
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


preferred_team_name = (
    st.session_state.pop(
        "preferred_team_name",
        None,
    )
)

if (
    preferred_team_name
    and preferred_team_name
    in team_lookup
):
    selected_team_name = (
        preferred_team_name
    )


selected_team = team_lookup[
    selected_team_name
]


# -------------------------------------------------
# TEAM SUMMARY
# -------------------------------------------------

col_team_1, col_team_2 = st.columns(
    2
)

with col_team_1:
    st.subheader(
        selected_team[
            "team_name"
        ]
    )

    st.write(
        "**Default formation:**",
        selected_team[
            "default_formation"
        ]
        or "Not set",
    )

with col_team_2:
    st.write(
        "**Tactical identity:**"
    )

    st.write(
        selected_team[
            "tactical_identity"
        ]
        or "Not set"
    )


st.divider()


# -------------------------------------------------
# MATCH SCENARIO
# -------------------------------------------------

st.header(
    "1. Match Scenario"
)

with st.form(
    "scenario_form"
):
    score_col_1, score_col_2, score_col_3 = (
        st.columns(
            3
        )
    )

    with score_col_1:
        minute = st.number_input(
            "Minute",
            min_value=0,
            max_value=130,
            value=68,
            step=1,
        )

    with score_col_2:
        our_score = st.number_input(
            "Our score",
            min_value=0,
            max_value=30,
            value=1,
            step=1,
        )

    with score_col_3:
        opponent_score = st.number_input(
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

    formation_col_1, formation_col_2 = (
        st.columns(
            2
        )
    )

    with formation_col_1:
        our_formation = st.text_input(
            "Our formation",
            value=(
                selected_team[
                    "default_formation"
                ]
                or "4-2-3-1"
            ),
        )

    with formation_col_2:
        opponent_formation = st.text_input(
            "Opponent formation",
            value="4-3-3",
        )

    tactical_problem = st.text_area(
        "What tactical problem are you seeing?",
        placeholder=(
            "Their right winger is repeatedly "
            "getting behind our left-back."
        ),
        height=100,
    )

    objective = st.text_area(
        "What is your objective?",
        placeholder=(
            "Protect the lead without completely "
            "losing our attacking threat."
        ),
        height=90,
    )

    coach_observations = st.text_area(
        "Coach observations",
        placeholder=(
            "Our left-back is booked and their "
            "right-back is beginning to overlap."
        ),
        height=100,
    )

    yellow_cards_text = st.text_input(
        "Yellow-carded roles",
        placeholder=(
            "Left-back, Defensive midfielder"
        ),
        help=(
            "Separate multiple roles with commas."
        ),
    )

    red_cards_text = st.text_input(
        "Red-carded roles",
        placeholder="",
        help=(
            "Separate multiple roles with commas."
        ),
    )

    substitutions_text = st.text_input(
        "Available substitutions / roles",
        placeholder=(
            "Centre-back, Left-back, "
            "Defensive midfielder"
        ),
        help=(
            "Separate multiple roles with commas."
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
    if (
        len(
            tactical_problem.strip()
        )
        < 10
    ):
        st.error(
            "Describe the tactical problem "
            "in a little more detail."
        )

    elif (
        len(
            objective.strip()
        )
        < 5
    ):
        st.error(
            "Enter the tactical objective."
        )

    else:
        reset_analysis()

        def comma_list(
            value: str,
        ) -> list[str]:
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

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
            "yellow_cards": comma_list(
                yellow_cards_text
            ),
            "red_cards": comma_list(
                red_cards_text
            ),
            "available_substitutions": (
                comma_list(
                    substitutions_text
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
                    f"scenarios/"
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


# -------------------------------------------------
# DECISION BRIEF
# -------------------------------------------------

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

    summary_col_1, summary_col_2, summary_col_3 = (
        st.columns(
            3
        )
    )

    with summary_col_1:
        st.metric(
            "Scenario profile",
            brief[
                "scenario_profile"
            ].replace(
                "_",
                " ",
            ).title(),
        )

    with summary_col_2:
        st.metric(
            "Confidence",
            brief[
                "confidence"
            ].title(),
        )

    with summary_col_3:
        st.metric(
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

    options = brief[
        "options"
    ]

    for option in options:
        is_leader = (
            option[
                "option_id"
            ]
            == brief[
                "leading_option_id"
            ]
        )

        heading = option_score_label(
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

            score_columns = (
                st.columns(
                    4
                )
            )

            score_items = list(
                option[
                    "scores"
                ].items()
            )

            for index, (
                name,
                score,
            ) in enumerate(
                score_items
            ):
                with score_columns[
                    index % 4
                ]:
                    st.metric(
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
                st.write(
                    "**Strengths**"
                )

                for item in option[
                    "strengths"
                ]:
                    st.write(
                        f"• {item}"
                    )

            with right:
                st.write(
                    "**Risks**"
                )

                for item in option[
                    "risks"
                ]:
                    st.write(
                        f"• {item}"
                    )

            st.write(
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


    # ---------------------------------------------
    # COACH SELECTION
    # ---------------------------------------------

    st.divider()

    st.header(
        "3. Coach Decision"
    )

    selection_result = (
        st.session_state.get(
            "selection_result"
        )
    )

    if selection_result:
        st.success(
            "Coach selection saved."
        )

        st.write(
            "**Selected option:**",
            selection_result[
                "selected_option_id"
            ],
        )

        if selection_result[
            "rationale"
        ]:
            st.write(
                "**Rationale:**",
                selection_result[
                    "rationale"
                ],
            )

    else:
        option_lookup = {
            option_score_label(
                option
            ): option[
                "option_id"
            ]
            for option in options
        }

        with st.form(
            "coach_selection_form"
        ):
            chosen_label = st.radio(
                "Select the option you want to implement",
                options=list(
                    option_lookup
                ),
            )

            rationale = st.text_area(
                "Coach rationale",
                placeholder=(
                    "Why are you choosing this option?"
                ),
                max_chars=1500,
            )

            save_selection_clicked = (
                st.form_submit_button(
                    "Save Coach Decision",
                    type="primary",
                    use_container_width=True,
                )
            )

        if save_selection_clicked:
            selected_option_id = (
                option_lookup[
                    chosen_label
                ]
            )

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
                            selected_option_id
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