"""GET /nowcast -- thunderstorm nowcast endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.nowcast import Nowcast
from app.services.nowcast_adapter import run_nowcast

router = APIRouter(prefix="/nowcast", tags=["nowcast"])

def serialize_nowcast(nowcast: Nowcast) -> dict:
    centroid_lat, centroid_lon, radius_km = 20.0, 80.0, 20.0
    try:
        if nowcast.affected_area is not None:
            shape = to_shape(nowcast.affected_area)
            centroid_lon = shape.centroid.x
            centroid_lat = shape.centroid.y
            # rough estimate of radius based on polygon bounds
            minx, miny, maxx, maxy = shape.bounds
            # roughly convert degree to km (1 deg ~ 111km)
            radius_km = max(maxx - minx, maxy - miny) * 111 / 2
    except Exception:
        pass

    return {
        "cell_id": str(nowcast.id),
        "run_time": nowcast.run_time.isoformat() if nowcast.run_time else None,
        "lead_time_minutes": nowcast.lead_time_minutes,
        "severity": nowcast.storm_intensity_class,
        "probability": nowcast.probability,
        "details": nowcast.details,
        "center": {"lat": centroid_lat, "lon": centroid_lon},
        "radius_km": max(10, radius_km)
    }

@router.get("/")
async def get_latest_nowcast(db: AsyncSession = Depends(get_db)) -> dict:
    """Return the latest thunderstorm nowcasts."""
    stmt = select(Nowcast).order_by(Nowcast.run_time.desc()).limit(10)
    result = await db.execute(stmt)
    nowcasts = result.scalars().all()
    
    return {
        "nowcasts": [serialize_nowcast(n) for n in nowcasts],
        "count": len(nowcasts)
    }

@router.get("/{nowcast_id}")
async def get_nowcast_by_id(nowcast_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """Return a specific nowcast by ID."""
    stmt = select(Nowcast).where(Nowcast.id == nowcast_id)
    result = await db.execute(stmt)
    nowcast = result.scalars().first()
    
    if not nowcast:
        raise HTTPException(status_code=404, detail="Nowcast not found")
        
    return serialize_nowcast(nowcast)

@router.post("/trigger")
async def trigger_nowcast() -> dict:
    """Manually trigger a new nowcast cycle."""
    # Run data fusion + ML inference pipeline (stubbed)
    result = run_nowcast()
    return {"status": "ok", "nowcast": result}
