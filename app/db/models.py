from __future__ import annotations

from uuid import uuid4
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VehicleModel(Base):
    __tablename__ = "vehicle_models"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid4)

    year: Mapped[int] = mapped_column(Integer, nullable=False)
    make: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    trim: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Nice URL key, e.g. 2018-toyota-camry-se
    canonical_key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # relationships (optional but useful)
    listings: Mapped[list["ListingSnapshot"]] = relationship(
        back_populates="vehicle_model",
        cascade="all, delete-orphan",
    )
    weekly_stats: Mapped[list["ModelWeeklyStat"]] = relationship(
        back_populates="vehicle_model",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_vehicle_models_year_make_model", "year", "make", "model"),
    )


class ListingSnapshot(Base):
    __tablename__ = "listing_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid4)

    vehicle_model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicle_models.id", ondelete="CASCADE"),
        nullable=False,
    )

    # When you observed this listing (daily snapshot)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Asking price in USD cents is ideal, but for MVP use whole dollars.
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    mileage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Keep coarse location to start (state/metro)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Which pipeline produced it: "dataset", "marketcheck", etc.
    source: Mapped[str] = mapped_column(String(32), nullable=False)

    # Source-specific ID used to dedupe
    source_listing_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vehicle_model: Mapped["VehicleModel"] = relationship(back_populates="listings")

    __table_args__ = (
        # Helps avoid duplicate inserts for the same listing on the same day
        UniqueConstraint(
            "snapshot_date", "source", "source_listing_id",
            name="uq_listing_snapshots_snapshot_source_listingid",
        ),
        Index("ix_listing_snapshots_model_date", "vehicle_model_id", "snapshot_date"),
        Index("ix_listing_snapshots_snapshot_date", "snapshot_date"),
        Index("ix_listing_snapshots_source_listing", "source", "source_listing_id"),
    )


class ModelWeeklyStat(Base):
    __tablename__ = "model_weekly_stats"

    vehicle_model_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("vehicle_models.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Monday (or Sunday) of the week; you choose a convention and stick to it.
    week_start: Mapped[date] = mapped_column(Date, primary_key=True)

    median_price: Mapped[int] = mapped_column(Integer, nullable=False)
    p10_price: Mapped[int] = mapped_column(Integer, nullable=False)
    p90_price: Mapped[int] = mapped_column(Integer, nullable=False)
    listing_count: Mapped[int] = mapped_column(Integer, nullable=False)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vehicle_model: Mapped["VehicleModel"] = relationship(back_populates="weekly_stats")

    __table_args__ = (
        Index("ix_model_weekly_stats_week_start", "week_start"),
    )