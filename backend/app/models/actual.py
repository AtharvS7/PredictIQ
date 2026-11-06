"""
SQLAlchemy and Pydantic models for project actuals (Actuals Flywheel — CP06).
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.schemas.actual import ActualCreate, ActualResponse, ProjectsV2ExportItem


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""
    pass


class EstimateActual(Base):
    """SQLAlchemy model for the estimate_actuals table."""

    __tablename__ = "estimate_actuals"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    estimate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("estimates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actual_effort_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    actual_cost_usd: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    actual_duration_months: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    team_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    functional_size_delivered: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    consent_for_training: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by_user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )


__all__ = [
    "Base",
    "EstimateActual",
    "ActualCreate",
    "ActualResponse",
    "ProjectsV2ExportItem",
]
