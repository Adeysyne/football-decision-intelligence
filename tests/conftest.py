import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import (
    Base,
    get_db,
)
from app.main import app

# Ensure every mapped table is registered.
from app.db import models  # noqa: F401


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


@pytest.fixture(autouse=True)
def isolated_database():
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