from datetime import date
from typing import Optional
from uuid import UUID

from app.schemas.base import APIModel


class LatestSnapshotOut(APIModel):
    snapshot_date: date
    price: int
    mileage: Optional[int] = None
    region: Optional[str] = None
    source: str


class LatestWeeklyStatOut(APIModel):
    week_start: date
    median_price: int
    p10_price: int
    p90_price: int
    listing_count: int


class ModelCardOut(APIModel):
    id: UUID
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    canonical_key: str

    last_listing: Optional[LatestSnapshotOut] = None
    market: Optional[LatestWeeklyStatOut] = None