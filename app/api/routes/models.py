from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import VehicleModel
from app.schemas.models import VehicleModelOut

from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select

from datetime import date, timedelta
from sqlalchemy import select
from app.db.models import ModelWeeklyStat
from app.schemas.stats import ModelWeeklyStatOut

from app.services.aggregation import recompute_weekly_stats

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[VehicleModelOut])
def search_models(
    q: str | None = Query(default=None, min_length=1, description="Search make/model/trim/key"),
    year: int | None = Query(default=None, ge=1886, le=2100),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    stmt = select(VehicleModel)

    if year is not None:
        stmt = stmt.where(VehicleModel.year == year)

    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                VehicleModel.make.ilike(like),
                VehicleModel.model.ilike(like),
                VehicleModel.trim.ilike(like),
                VehicleModel.canonical_key.ilike(like),
            )
        )

    stmt = stmt.order_by(
        VehicleModel.year.desc(),
        VehicleModel.make.asc(),
        VehicleModel.model.asc(),
        VehicleModel.trim.asc().nulls_last(),
    ).limit(limit)

    return db.execute(stmt).scalars().all()

@router.get("/{model_id}", response_model=VehicleModelOut)
def get_model(
    model_id: UUID,
    db: Session = Depends(get_db),
):
    stmt = select(VehicleModel).where(VehicleModel.id == model_id)
    model = db.execute(stmt).scalar_one_or_none()

    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")

    return model

@router.get("/{model_id}/stats", response_model=list[ModelWeeklyStatOut])
def get_model_stats(
    model_id: UUID,
    range: str = "12w",  # e.g. 12w, 6m, 1y
    db: Session = Depends(get_db),
):
    today = date.today()

    if range == "12w":
        start = today - timedelta(weeks=12)
    elif range == "6m":
        start = today - timedelta(days=183)
    elif range == "1y":
        start = today - timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid range (use 12w, 6m, 1y)")

    stmt = (
        select(ModelWeeklyStat)
        .where(ModelWeeklyStat.vehicle_model_id == model_id)
        .where(ModelWeeklyStat.week_start >= start)
        .order_by(ModelWeeklyStat.week_start.asc())
    )
    return db.execute(stmt).scalars().all()

@router.post("/{model_id}/stats/recompute")
def recompute_stats(model_id: UUID, db: Session = Depends(get_db)):
    recompute_weekly_stats(db, str(model_id))
    return {"status": "ok"}