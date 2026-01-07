from typing import Optional
from uuid import UUID
from app.schemas.base import APIModel

class VehicleModelOut(APIModel):
    id: UUID
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    canonical_key: str