import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.config import (
    get_settings,
)
from app.core.request_context import (
    get_request_id,
)
from app.db.database import (
    get_db,
)
from app.models.scenario import (
    ScenarioCreate,
)
from app.services.ai_observability import (
    complete_ai_analysis_run,
    start_ai_analysis_run,
    summarize_usage,
)
from app.services.ai_orchestration import (
    analyse_with_verification,
)
from app.services.ai_reasoning import (
    AIAnalysisError,
    analyse_with_ai,
)


logger = logging.getLogger(
    "fdi.ai"
)


router = APIRouter(
    prefix="/api/v1/ai",
    tags=[
        "AI analysis"
    ],
)


def _start_observability(
    *,
    scenario: ScenarioCreate,
    db: Session,
):
    settings = get_settings()

    try:
        run = start_ai_analysis_run(
            team_name=(
                scenario.team_name
            ),
            model_name=(
                settings.openai_model
            ),
            db=db,
        )

        logger.info(
            "verified_ai_started",
            extra={
                "event": (
                    "verified_ai_started"
                ),
                "request_id": (
                    get_request_id()
                ),
                "analysis_run_id": str(
                    run.analysis_run_id
                ),
                "team_name": (
                    scenario.team_name
                ),
                "model_name": (
                    settings.openai_model
                ),
            },
        )

        return run

    except Exception:
        db.rollback()

        logger.error(
            "ai_observability_start_failed",
            extra={
                "event": (
                    "ai_observability_start_failed"
                ),
                "request_id": (
                    get_request_id()
                ),
                "team_name": (
                    scenario.team_name
                ),
                "error_type": (
                    "ObservabilityFailure"
                ),
            },
        )

        return None


def _complete_observability(
    *,
    run,
    db: Session,
    status: str,
    verification_status: (
        str | None
    ),
    revised: bool,
    review_attempt_count: int,
    input_tokens: int | None,
    output_tokens: int | None,
    total_tokens: int | None,
    error_type: str | None,
    error_message: str | None,
) -> None:
    if run is None:
        return

    try:
        complete_ai_analysis_run(
            analysis_run_id=(
                run.analysis_run_id
            ),
            status=status,
            verification_status=(
                verification_status
            ),
            revised=revised,
            review_attempt_count=(
                review_attempt_count
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=None,
            error_type=error_type,
            error_message=error_message,
            db=db,
        )

    except Exception:
        db.rollback()

        logger.error(
            "ai_observability_completion_failed",
            extra={
                "event": (
                    "ai_observability_completion_failed"
                ),
                "request_id": (
                    get_request_id()
                ),
                "analysis_run_id": str(
                    run.analysis_run_id
                ),
                "error_type": (
                    "ObservabilityFailure"
                ),
            },
        )


def _failure_metadata(
    exc: AIAnalysisError,
) -> dict:
    message = str(
        exc
    )

    if (
        "could not be verified"
        in message.lower()
    ):
        return {
            "status": (
                "verification_failed"
            ),
            "verification_status": (
                "needs_revision"
            ),
            "revised": True,
            "review_attempt_count": 2,
            "error_type": (
                "VerificationFailure"
            ),
        }

    if exc.status_code == 503:
        return {
            "status": (
                "provider_failed"
            ),
            "verification_status": None,
            "revised": False,
            "review_attempt_count": 0,
            "error_type": (
                "ProviderFailure"
            ),
        }

    return {
        "status": "failed",
        "verification_status": None,
        "revised": False,
        "review_attempt_count": 0,
        "error_type": (
            "AIAnalysisError"
        ),
    }


@router.post(
    "/analyse"
)
def analyse_scenario(
    scenario: ScenarioCreate,
) -> dict:
    try:
        return analyse_with_ai(
            scenario
        )

    except AIAnalysisError as exc:
        logger.warning(
            "ai_analysis_failed",
            extra={
                "event": (
                    "ai_analysis_failed"
                ),
                "request_id": (
                    get_request_id()
                ),
                "team_name": (
                    scenario.team_name
                ),
                "error_type": (
                    type(
                        exc
                    ).__name__
                ),
            },
        )

        raise HTTPException(
            status_code=(
                exc.status_code
            ),
            detail=str(
                exc
            ),
        ) from None


@router.post(
    "/analyse-verified"
)
def analyse_verified_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(
        get_db
    ),
) -> dict:
    run = _start_observability(
        scenario=scenario,
        db=db,
    )

    try:
        result = (
            analyse_with_verification(
                scenario
            )
        )

    except AIAnalysisError as exc:
        failure = (
            _failure_metadata(
                exc
            )
        )

        _complete_observability(
            run=run,
            db=db,
            status=(
                failure[
                    "status"
                ]
            ),
            verification_status=(
                failure[
                    "verification_status"
                ]
            ),
            revised=(
                failure[
                    "revised"
                ]
            ),
            review_attempt_count=(
                failure[
                    "review_attempt_count"
                ]
            ),
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            error_type=(
                failure[
                    "error_type"
                ]
            ),
            error_message=str(
                exc
            ),
        )

        logger.warning(
            "verified_ai_failed",
            extra={
                "event": (
                    "verified_ai_failed"
                ),
                "request_id": (
                    get_request_id()
                ),
                "analysis_run_id": (
                    str(
                        run.analysis_run_id
                    )
                    if run
                    else None
                ),
                "team_name": (
                    scenario.team_name
                ),
                "status_code": (
                    exc.status_code
                ),
                "verification_status": (
                    failure[
                        "verification_status"
                    ]
                ),
                "revised": (
                    failure[
                        "revised"
                    ]
                ),
                "review_attempt_count": (
                    failure[
                        "review_attempt_count"
                    ]
                ),
                "error_type": (
                    failure[
                        "error_type"
                    ]
                ),
            },
        )

        raise HTTPException(
            status_code=(
                exc.status_code
            ),
            detail=str(
                exc
            ),
        ) from None

    except Exception as exc:
        _complete_observability(
            run=run,
            db=db,
            status="failed",
            verification_status=None,
            revised=False,
            review_attempt_count=0,
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            error_type=(
                "UnexpectedFailure"
            ),
            error_message=(
                "Unexpected verified "
                "analysis failure."
            ),
        )

        logger.error(
            "verified_ai_unexpected_failure",
            extra={
                "event": (
                    "verified_ai_unexpected_failure"
                ),
                "request_id": (
                    get_request_id()
                ),
                "analysis_run_id": (
                    str(
                        run.analysis_run_id
                    )
                    if run
                    else None
                ),
                "team_name": (
                    scenario.team_name
                ),
                "error_type": (
                    type(
                        exc
                    ).__name__
                ),
            },
        )

        raise

    verification = result.get(
        "verification",
        {},
    )

    review_attempts = (
        verification.get(
            "review_attempts",
            [],
        )
        or []
    )

    usage = summarize_usage(
        result.get(
            "usage"
        )
    )

    _complete_observability(
        run=run,
        db=db,
        status="approved",
        verification_status=(
            verification.get(
                "status",
                "approved",
            )
        ),
        revised=bool(
            verification.get(
                "revised",
                False,
            )
        ),
        review_attempt_count=len(
            review_attempts
        ),
        input_tokens=(
            usage[
                "input_tokens"
            ]
        ),
        output_tokens=(
            usage[
                "output_tokens"
            ]
        ),
        total_tokens=(
            usage[
                "total_tokens"
            ]
        ),
        error_type=None,
        error_message=None,
    )

    logger.info(
        "verified_ai_completed",
        extra={
            "event": (
                "verified_ai_completed"
            ),
            "request_id": (
                get_request_id()
            ),
            "analysis_run_id": (
                str(
                    run.analysis_run_id
                )
                if run
                else None
            ),
            "team_name": (
                scenario.team_name
            ),
            "model_name": (
                result.get(
                    "models",
                    {},
                ).get(
                    "reasoning"
                )
            ),
            "verification_status": (
                verification.get(
                    "status",
                    "approved",
                )
            ),
            "revised": bool(
                verification.get(
                    "revised",
                    False,
                )
            ),
            "review_attempt_count": (
                len(
                    review_attempts
                )
            ),
            "total_tokens": (
                usage[
                    "total_tokens"
                ]
            ),
        },
    )

    response = dict(
        result
    )

    if run is not None:
        response[
            "analysis_run_id"
        ] = str(
            run.analysis_run_id
        )

    return response