"""GET /radar -- radar data query endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.radar_scan import RadarScan

router = APIRouter(prefix="/radar", tags=["radar"])

def serialize_radar_scan(scan: RadarScan) -> dict:
    min_lat, min_lon, max_lat, max_lon = None, None, None, None
    try:
        if scan.bbox is not None:
            shape = to_shape(scan.bbox)
            min_lon, min_lat, max_lon, max_lat = shape.bounds
    except Exception:
        pass
        
    return {
        "id": str(scan.id),
        "station_id": scan.station_id,
        "scan_time": scan.scan_time.isoformat() if scan.scan_time else None,
        "file_path": scan.file_path,
        "bbox": {
            "min_lat": min_lat,
            "min_lon": min_lon,
            "max_lat": max_lat,
            "max_lon": max_lon
        }
    }

@router.get("/latest")
async def get_latest_radar(db: AsyncSession = Depends(get_db)) -> dict:
    """Return metadata for the latest radar scans across all stations."""
    # Note: Postgres DISTINCT ON maps to distinct() in sqlalchemy
    stmt = (
        select(RadarScan)
        .distinct(RadarScan.station_id)
        .order_by(RadarScan.station_id, RadarScan.scan_time.desc())
    )
    result = await db.execute(stmt)
    scans = result.scalars().all()
    
    return {"scans": [serialize_radar_scan(s) for s in scans], "count": len(scans)}

@router.get("/station/{station_id}")
async def get_radar_by_station(station_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """Return recent radar scans for a specific DWR station."""
    stmt = (
        select(RadarScan)
        .where(RadarScan.station_id == station_id)
        .order_by(RadarScan.scan_time.desc())
        .limit(20)
    )
    result = await db.execute(stmt)
    scans = result.scalars().all()
    
    return {"station_id": station_id, "scans": [serialize_radar_scan(s) for s in scans]}
