import json
import logging
from uuid import UUID

from fastapi.testclient import (
    TestClient,
)

import app.main as main_module
from app.core.logging_config import (
    JSONFormatter,
)
from app.main import app


client = TestClient(
    app
)


def test_health_returns_request_id():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None

    UUID(
        request_id
    )


def test_root_returns_request_id():
    response = client.get(
        "/"
    )

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None

    UUID(
        request_id
    )


def test_beta_rejection_returns_request_id(
    monkeypatch,
):
    monkeypatch.setattr(
        main_module.settings,
        "beta_access_code",
        "test-beta-code",
    )

    response = client.get(
        "/api/v1/teams"
    )

    assert response.status_code == 401

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None

    UUID(
        request_id
    )


def test_json_formatter_uses_safe_allowlist():
    formatter = JSONFormatter()

    record = logging.LogRecord(
        name="fdi.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="test_event",
        args=(),
        exc_info=None,
    )

    record.event = (
        "test_event"
    )

    record.request_id = (
        "request-123"
    )

    record.openai_api_key = (
        "secret-key-must-not-log"
    )

    record.beta_access_code = (
        "secret-beta-code"
    )

    record.admin_access_code = (
        "secret-admin-code"
    )

    rendered = formatter.format(
        record
    )

    payload = json.loads(
        rendered
    )

    assert (
        payload[
            "event"
        ]
        == "test_event"
    )

    assert (
        payload[
            "request_id"
        ]
        == "request-123"
    )

    assert (
        "secret-key-must-not-log"
        not in rendered
    )

    assert (
        "secret-beta-code"
        not in rendered
    )

    assert (
        "secret-admin-code"
        not in rendered
    )