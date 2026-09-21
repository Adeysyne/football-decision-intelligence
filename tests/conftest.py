import importlib

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401
from app.db.database import (
    Base,
    get_db,
)
from app.main import app


main_module = importlib.import_module(
    "app.main"
)


test_engine = create_engine(
    "sqlite://",
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(
    autouse=True
)
def isolated_database():
    original_beta_access_code = (
        main_module.settings.beta_access_code
    )

    main_module.settings.beta_access_code = ""

    Base.metadata.create_all(
        bind=test_engine
    )

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db

        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    yield

    app.dependency_overrides.clear()

    Base.metadata.drop_all(
        bind=test_engine
    )

    main_module.settings.beta_access_code = (
        original_beta_access_code
    )