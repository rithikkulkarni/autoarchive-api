from sqlalchemy import text
from sqlalchemy.orm import Session


UPSERT_WEEKLY_SQL = """
INSERT INTO model_weekly_stats (
  vehicle_model_id,
  week_start,
  median_price,
  p10_price,
  p90_price,
  listing_count,
  computed_at
)
SELECT
  vehicle_model_id,
  date_trunc('week', snapshot_date)::date AS week_start,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY price)::int AS median_price,
  percentile_cont(0.1) WITHIN GROUP (ORDER BY price)::int AS p10_price,
  percentile_cont(0.9) WITHIN GROUP (ORDER BY price)::int AS p90_price,
  count(*)::int AS listing_count,
  now() AS computed_at
FROM listing_snapshots
WHERE vehicle_model_id = :model_id
GROUP BY vehicle_model_id, date_trunc('week', snapshot_date)
ON CONFLICT (vehicle_model_id, week_start)
DO UPDATE SET
  median_price = EXCLUDED.median_price,
  p10_price = EXCLUDED.p10_price,
  p90_price = EXCLUDED.p90_price,
  listing_count = EXCLUDED.listing_count,
  computed_at = EXCLUDED.computed_at;
"""


def recompute_weekly_stats(db: Session, model_id: str) -> None:
    db.execute(text(UPSERT_WEEKLY_SQL), {"model_id": model_id})
    db.commit()