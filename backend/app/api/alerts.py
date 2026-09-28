"""GET /alerts -- active thunderstorm alert endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.alert import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])

def serialize_alert(alert: Alert) -> dict:
    """Convert Alert ORM object to a JSON-serializable dict."""
    # Extract centroid from PostGIS polygon for frontend display
    centroid_lat, centroid_lon = 20.0, 80.0
    try:
        if alert.alert_area is not None:
            shape = to_shape(alert.alert_area)
            centroid_lon = shape.centroid.x
            centroid_lat = shape.centroid.y
    except Exception:
        pass

    return {
        "id": str(alert.id),
        "nowcast_id": str(alert.nowcast_id),
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "issue_time": alert.issue_time.isoformat() if alert.issue_time else None,
        "valid_until": alert.valid_until.isoformat() if alert.valid_until else None,
        "message": alert.message,
        "centroid_lat": centroid_lat,
        "centroid_lon": centroid_lon,
    }

@router.get("/")
async def get_active_alerts(db: AsyncSession = Depends(get_db)) -> dict:
    """Return all currently active thunderstorm alerts."""
    now = datetime.now(timezone.utc)
    stmt = select(Alert).where(Alert.valid_until > now).order_by(Alert.issue_time.desc())
    result = await db.execute(stmt)
    alerts = result.scalars().all()
    
    return {
        "alerts": [serialize_alert(a) for a in alerts],
        "count": len(alerts),
    }

@router.get("/{alert_id}")
async def get_alert_by_id(alert_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    """Return a specific alert by ID."""
    stmt = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(stmt)
    alert = result.scalars().first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    return serialize_alert(alert)
