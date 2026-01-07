from typing import List, Optional
from app.schemas.base import APIModel


class MileageHistogramOut(APIModel):
    bin_edges: list[int]
    counts: list[int]
    sample_size: int
    min_mileage: int | None = None
    max_mileage: int | None = None