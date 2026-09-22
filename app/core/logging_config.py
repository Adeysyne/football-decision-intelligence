import json
import logging
import sys
from datetime import (
    datetime,
    timezone,
)


LOG_FIELDS = (
    "event",
    "request_id",
    "method",
    "path",
    "status_code",
    "latency_ms",
    "analysis_run_id",
    "team_name",
    "model_name",
    "verification_status",
    "revised",
    "review_attempt_count",
    "total_tokens",
    "error_type",
)


class JSONFormatter(
    logging.Formatter
):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload: dict = {
            "timestamp": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "level": (
                record.levelname
            ),
            "logger": (
                record.name
            ),
            "message": (
                record.getMessage()
            ),
        }

        for field in LOG_FIELDS:
            value = getattr(
                record,
                field,
                None,
            )

            if value is not None:
                payload[
                    field
                ] = value

        if record.exc_info:
            exception_type = (
                record.exc_info[
                    0
                ]
            )

            if exception_type:
                payload[
                    "exception_type"
                ] = (
                    exception_type.__name__
                )

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )


def configure_logging() -> None:
    logger = logging.getLogger(
        "fdi"
    )

    logger.setLevel(
        logging.INFO
    )

    logger.propagate = False

    if logger.handlers:
        return

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JSONFormatter()
    )

    logger.addHandler(
        handler
    )