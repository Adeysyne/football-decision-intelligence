from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base


class ScenarioRecord(Base):
    __tablename__ = "scenarios"

    scenario_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    team_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    opponent_name: Mapped[
        str | None
    ] = mapped_column(
        String(100),
        nullable=True,
    )

    minute: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    our_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    opponent_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    our_formation: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    opponent_formation: Mapped[
        str | None
    ] = mapped_column(
        String(20),
        nullable=True,
    )

    tactical_problem: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    coach_observations: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    scenario_payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )