"""GET /lightning -- lightning stroke query endpoints."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.lightning_event import LightningEvent

router = APIRouter(prefix="/lightning", tags=["lightning"])

def serialize_lightning(stroke: LightningEvent) -> dict:
    lat, lon = 0.0, 0.0
    try:
        if stroke.location is not None:
            shape = to_shape(stroke.location)
            lon = shape.x
            lat = shape.y
    except Exception:
        pass

    return {
        "id": str(stroke.id),
        "event_time": stroke.event_time.isoformat() if stroke.event_time else None,
        "lat": lat,
        "lon": lon,
        "current_ka": stroke.current_ka,
        "polarity": stroke.polarity
    }

@router.get("/recent")
async def get_recent_lightning(
    minutes: int = 15,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Return recent lightning stroke data (last N minutes)."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=minutes)
    
    stmt = (
        select(LightningEvent)
        .where(LightningEvent.event_time >= since)
        .order_by(LightningEvent.event_time.desc())
        .limit(1000)
    )
    result = await db.execute(stmt)
    strokes = result.scalars().all()
    
    return {"strokes": [serialize_lightning(s) for s in strokes], "count": len(strokes)}

@router.get("/density")
async def get_lightning_density(
    lat_min: float = 20.0,
    lat_max: float = 30.0,
    lon_min: float = 70.0,
    lon_max: float = 85.0,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Return lightning density grid for a bounding box."""
    # TODO: In PostGIS, we would use ST_MakeEnvelope and group by ST_SnapToGrid
    return {
        "bbox": {"lat_min": lat_min, "lat_max": lat_max, "lon_min": lon_min, "lon_max": lon_max},
        "density_grid": [],
        "message": "Density grid computation pending PostGIS integration."
    }
