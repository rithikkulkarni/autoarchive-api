from datetime import date, datetime
from uuid import UUID

from app.schemas.base import APIModel


class ModelWeeklyStatOut(APIModel):
    vehicle_model_id: UUID
    week_start: date
    median_price: int
    p10_price: int
    p90_price: int
    listing_count: int
    computed_at: datetime