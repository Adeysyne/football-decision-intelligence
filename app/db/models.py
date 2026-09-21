from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
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


class TeamRecord(Base):
    __tablename__ = "teams"

    team_id: Mapped[str] = mapped_column(
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    team_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    default_formation: Mapped[
        str | None
    ] = mapped_column(
        String(20),
        nullable=True,
    )

    tactical_identity: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )


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


class DecisionRecord(Base):
    __tablename__ = "decisions"

    decision_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    scenario_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "scenarios.scenario_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    scenario_profile: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    leading_option_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    generated_from: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    decision_payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )


class CoachSelectionRecord(Base):
    __tablename__ = "coach_selections"

    selection_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    decision_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "decisions.decision_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    selected_option_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    selected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    rationale: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )


class DecisionOutcomeRecord(Base):
    __tablename__ = "decision_outcomes"

    outcome_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(
            uuid4()
        ),
    )

    decision_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey(
            "decisions.decision_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    final_our_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    final_opponent_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    coach_assessment: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    outcome_summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    observed_effects: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    next_time_notes: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )


class PilotInterestRecord(Base):
    __tablename__ = "pilot_interests"

    pilot_interest_id: Mapped[str] = mapped_column(
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

    coach_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        index=True,
    )

    club_or_team: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    would_use_in_real_matches: Mapped[str] = (
        mapped_column(
            String(10),
            nullable=False,
        )
    )

    join_private_pilot: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    willingness_to_pay_monthly_gbp: Mapped[
        int | None
    ] = mapped_column(
        Integer,
        nullable=True,
    )

    most_valuable_feature: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    feedback: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )