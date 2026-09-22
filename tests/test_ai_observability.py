from uuid import UUID

from app.services.ai_observability import (
    complete_ai_analysis_run,
    get_ai_analysis_run,
    start_ai_analysis_run,
)
from tests.conftest import (
    TestingSessionLocal,
)


def test_ai_analysis_run_can_start():
    with TestingSessionLocal() as db:
        result = start_ai_analysis_run(
            team_name="Observability FC",
            model_name="gpt-5.6-luna",
            db=db,
        )

        assert result.status == "started"

        assert (
            result.team_name
            == "Observability FC"
        )

        assert (
            result.model_name
            == "gpt-5.6-luna"
        )

        assert (
            result.completed_at
            is None
        )

        assert (
            result.latency_ms
            is None
        )


def test_ai_analysis_run_can_complete():
    with TestingSessionLocal() as db:
        started = start_ai_analysis_run(
            team_name="Observability FC",
            model_name="gpt-5.6-luna",
            db=db,
        )

        completed = (
            complete_ai_analysis_run(
                analysis_run_id=(
                    started.analysis_run_id
                ),
                status="approved",
                verification_status=(
                    "approved"
                ),
                revised=True,
                review_attempt_count=2,
                input_tokens=1200,
                output_tokens=450,
                total_tokens=1650,
                estimated_cost_usd=0.01,
                error_type=None,
                error_message=None,
                db=db,
            )
        )

        assert (
            completed.status
            == "approved"
        )

        assert (
            completed.verification_status
            == "approved"
        )

        assert completed.revised is True

        assert (
            completed.review_attempt_count
            == 2
        )

        assert (
            completed.input_tokens
            == 1200
        )

        assert (
            completed.output_tokens
            == 450
        )

        assert (
            completed.total_tokens
            == 1650
        )

        assert (
            completed.latency_ms
            is not None
        )

        assert (
            completed.latency_ms
            >= 0
        )


def test_failed_verification_is_recorded():
    with TestingSessionLocal() as db:
        started = start_ai_analysis_run(
            team_name="Observability FC",
            model_name="gpt-5.6-luna",
            db=db,
        )

        completed = (
            complete_ai_analysis_run(
                analysis_run_id=(
                    started.analysis_run_id
                ),
                status=(
                    "verification_failed"
                ),
                verification_status=(
                    "needs_revision"
                ),
                revised=True,
                review_attempt_count=2,
                input_tokens=1000,
                output_tokens=500,
                total_tokens=1500,
                estimated_cost_usd=None,
                error_type=(
                    "VerificationFailure"
                ),
                error_message=(
                    "The response did not "
                    "pass final verification."
                ),
                db=db,
            )
        )

        assert (
            completed.status
            == "verification_failed"
        )

        assert (
            completed.error_type
            == "VerificationFailure"
        )

        assert (
            completed.error_message
            is not None
        )


def test_ai_analysis_run_can_be_retrieved():
    with TestingSessionLocal() as db:
        started = start_ai_analysis_run(
            team_name="Observability FC",
            model_name="gpt-5.6-luna",
            db=db,
        )

        result = get_ai_analysis_run(
            analysis_run_id=UUID(
                str(
                    started.analysis_run_id
                )
            ),
            db=db,
        )

        assert result is not None

        assert (
            result.analysis_run_id
            == started.analysis_run_id
        )


def test_unknown_ai_analysis_run_returns_none():
    with TestingSessionLocal() as db:
        result = get_ai_analysis_run(
            analysis_run_id=UUID(
                "11111111-1111-1111-1111-111111111111"
            ),
            db=db,
        )

        assert result is None