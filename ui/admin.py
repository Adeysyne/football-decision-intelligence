import os

import httpx
import streamlit as st


API_BASE_URL = os.getenv(
    "FDI_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

COACH_UI_URL = os.getenv(
    "FDI_COACH_UI_URL",
    "http://localhost:8501",
).rstrip("/")


st.set_page_config(
    page_title="FDI Operations",
    page_icon="📊",
    layout="wide",
)


def api_request(
    method: str,
    path: str,
    *,
    admin_code: str | None = None,
    timeout: float = 30.0,
):
    headers: dict[str, str] = {}

    code = (
        admin_code
        if admin_code is not None
        else st.session_state.get(
            "admin_access_code",
            "",
        )
    )

    if code:
        headers[
            "X-Admin-Access-Code"
        ] = code

    try:
        response = httpx.request(
            method=method,
            url=f"{API_BASE_URL}{path}",
            headers=headers,
            timeout=timeout,
        )

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Could not connect to the "
            "Football Decision Intelligence API."
        ) from exc

    if response.status_code >= 400:
        try:
            body = response.json()

            detail = body.get(
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


def format_latency(
    latency_ms: float | None,
) -> str:
    if latency_ms is None:
        return "—"

    if latency_ms >= 1000:
        return (
            f"{latency_ms / 1000:.2f}s"
        )

    return f"{latency_ms:.0f}ms"


def format_number(
    value: int | float | None,
) -> str:
    if value is None:
        return "—"

    return f"{value:,.0f}"


def format_status(
    value: str,
) -> str:
    return value.replace(
        "_",
        " ",
    ).title()


def status_icon(
    status: str,
) -> str:
    mapping = {
        "approved": "✅",
        "verification_failed": "⚠️",
        "provider_failed": "🔌",
        "failed": "❌",
        "started": "⏳",
    }

    return mapping.get(
        status,
        "•",
    )


st.title(
    "📊 Football Decision Intelligence — Operations"
)

st.caption(
    "Private operational monitoring for AI reliability, "
    "verification performance and usage."
)


try:
    api_request(
        "GET",
        "/health",
        admin_code="",
    )

except RuntimeError as exc:
    st.error(
        str(exc)
    )

    st.info(
        "The backend API must be running "
        "before the Operations Dashboard can load."
    )

    st.stop()


if not st.session_state.get(
    "admin_authenticated",
    False,
):
    st.subheader(
        "🔐 Administrator Access"
    )

    st.write(
        "This dashboard contains internal operational "
        "and AI-usage information and is not available "
        "to pilot users."
    )

    with st.form(
        "admin_login_form"
    ):
        entered_code = st.text_input(
            "Admin access code",
            type="password",
            placeholder=(
                "Enter administrator access code"
            ),
        )

        login_clicked = (
            st.form_submit_button(
                "Open Operations Dashboard",
                type="primary",
                use_container_width=True,
            )
        )

    if login_clicked:
        if not entered_code.strip():
            st.error(
                "Enter the administrator access code."
            )

        else:
            try:
                api_request(
                    "GET",
                    (
                        "/api/v1/operations/"
                        "ai-summary?window_days=30"
                    ),
                    admin_code=(
                        entered_code.strip()
                    ),
                )

                st.session_state[
                    "admin_access_code"
                ] = entered_code.strip()

                st.session_state[
                    "admin_authenticated"
                ] = True

                st.rerun()

            except RuntimeError:
                st.error(
                    "Administrator access was not accepted."
                )

    st.stop()


with st.sidebar:
    st.header(
        "Operations"
    )

    st.success(
        "Admin authenticated"
    )

    window_label = st.selectbox(
        "Monitoring window",
        [
            "Last 7 days",
            "Last 30 days",
            "Last 90 days",
            "Last 365 days",
        ],
        index=1,
    )

    window_map = {
        "Last 7 days": 7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 365 days": 365,
    }

    window_days = window_map[
        window_label
    ]

    if st.button(
        "Refresh dashboard",
        use_container_width=True,
    ):
        st.rerun()

    if st.button(
        "Lock / Sign out",
        use_container_width=True,
    ):
        st.session_state.clear()
        st.rerun()

    st.divider()

    st.caption(
        "Coach dashboard"
    )

    st.link_button(
        "Open Coach Dashboard",
        COACH_UI_URL,
        use_container_width=True,
    )

    st.caption(
        COACH_UI_URL
    )


try:
    summary = api_request(
        "GET",
        (
            "/api/v1/operations/"
            f"ai-summary?window_days={window_days}"
        ),
    )

except RuntimeError as exc:
    st.error(
        "Operations data could not be loaded."
    )

    with st.expander(
        "Technical detail"
    ):
        st.code(
            str(exc)
        )

    st.stop()


st.subheader(
    "AI Reliability Overview"
)

st.caption(
    f"Operational measurements from the "
    f"last {window_days} days."
)


col_1, col_2, col_3, col_4 = st.columns(
    4
)

col_1.metric(
    "AI analysis runs",
    summary[
        "total_runs"
    ],
)

col_2.metric(
    "Approval rate",
    (
        f"{summary['approval_rate_pct']:.2f}%"
    ),
)

col_3.metric(
    "Revision rate",
    (
        f"{summary['revision_rate_pct']:.2f}%"
    ),
)

col_4.metric(
    "Verification failure rate",
    (
        f"{summary['verification_failure_rate_pct']:.2f}%"
    ),
)


st.divider()

st.subheader(
    "Verification & Reliability"
)

col_1, col_2, col_3, col_4 = st.columns(
    4
)

col_1.metric(
    "Approved",
    summary[
        "approved_runs"
    ],
)

col_2.metric(
    "Verification failures",
    summary[
        "verification_failed_runs"
    ],
)

col_3.metric(
    "Provider failures",
    summary[
        "provider_failed_runs"
    ],
)

col_4.metric(
    "Unexpected failures",
    summary[
        "failed_runs"
    ],
)

if summary[
    "in_progress_runs"
]:
    st.info(
        f"{summary['in_progress_runs']} AI analysis "
        "run(s) are currently recorded as in progress."
    )


st.divider()

st.subheader(
    "Performance & Usage"
)

col_1, col_2, col_3, col_4 = st.columns(
    4
)

col_1.metric(
    "Average latency",
    format_latency(
        summary[
            "average_latency_ms"
        ]
    ),
)

col_2.metric(
    "Input tokens",
    format_number(
        summary[
            "input_tokens"
        ]
    ),
)

col_3.metric(
    "Output tokens",
    format_number(
        summary[
            "output_tokens"
        ]
    ),
)

col_4.metric(
    "Total tokens",
    format_number(
        summary[
            "total_tokens"
        ]
    ),
)


st.subheader(
    "AI Cost Monitoring"
)

estimated_cost = summary[
    "estimated_cost_usd"
]

if estimated_cost > 0:
    st.metric(
        "Estimated AI cost",
        f"${estimated_cost:,.4f}",
    )

else:
    st.info(
        "Token usage collection is active. "
        "Automated model-price calculation has not "
        "yet been configured, so this dashboard does "
        "not currently claim an AI cost figure."
    )


st.divider()

st.subheader(
    "Model Distribution"
)

model_counts = summary[
    "model_counts"
]

if model_counts:
    for (
        model_name,
        run_count,
    ) in model_counts.items():
        st.markdown(
            f"**{model_name}** — "
            f"{run_count:,} run(s)"
        )

else:
    st.caption(
        "No model usage has been recorded "
        "for this period."
    )


st.divider()

st.subheader(
    "Recent AI Analysis Runs"
)

recent_runs = summary[
    "recent_runs"
]

if not recent_runs:
    st.info(
        "No AI analysis runs were recorded "
        "during this monitoring window."
    )

else:
    table_rows = []

    for run in recent_runs:
        table_rows.append(
            {
                "Started": (
                    run[
                        "started_at"
                    ]
                ),
                "Team": (
                    run[
                        "team_name"
                    ]
                ),
                "Model": (
                    run[
                        "model_name"
                    ]
                ),
                "Status": (
                    f"{status_icon(run['status'])} "
                    f"{format_status(run['status'])}"
                ),
                "Verification": (
                    format_status(
                        run[
                            "verification_status"
                        ]
                    )
                    if run[
                        "verification_status"
                    ]
                    else "—"
                ),
                "Revised": (
                    "Yes"
                    if run[
                        "revised"
                    ]
                    else "No"
                ),
                "Reviews": (
                    run[
                        "review_attempt_count"
                    ]
                ),
                "Tokens": (
                    run[
                        "total_tokens"
                    ]
                    if run[
                        "total_tokens"
                    ] is not None
                    else "—"
                ),
                "Latency": (
                    format_latency(
                        run[
                            "latency_ms"
                        ]
                    )
                ),
                "Error": (
                    run[
                        "error_type"
                    ]
                    or "—"
                ),
            }
        )

    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )


st.divider()

st.subheader(
    "How to Interpret These Metrics"
)

st.markdown(
    """
**Approval rate** measures the proportion of completed
verified-AI requests that ultimately passed the verification
gate.

**Revision rate** measures how often the verifier required a
controlled revision before completion.

**Verification failure rate** measures how often an explanation
still failed after the permitted verification process.

**Latency** measures end-to-end verified-AI processing time,
including the reasoning and critic stages.

These metrics describe system behaviour. They do not measure
whether a tactical decision was objectively correct or caused
a match outcome.
"""
)


st.divider()

st.subheader(
    "Pilot Readiness"
)

total_runs = summary[
    "total_runs"
]

if total_runs < 10:
    st.warning(
        "The telemetry pipeline is operational, but the "
        "sample is still very small. Reliability percentages "
        "should not yet be treated as stable production "
        "performance estimates."
    )

else:
    st.info(
        "The system now has enough operational observations "
        "to begin looking for early reliability patterns, "
        "although larger real-user samples are still required."
    )