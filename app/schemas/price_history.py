from datetime import date
from app.schemas.base import APIModel


class PriceHistoryPoint(APIModel):
    week_start: date
    median_price: int
    p10_price: int
    p90_price: int
    listing_count: int