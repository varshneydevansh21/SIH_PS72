from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.alert import Alert
from app.services.alert_engine import generate_alerts, create_polygon_coords
from app.services.nowcast_adapter import run_nowcast

router = APIRouter(prefix="/alerts", tags=["alerts"])


def serialize_alert(alert: Alert) -> dict:
    centroid_lat, centroid_lon = 20.0, 80.0
    poly_coords = []
    try:
        if alert.alert_area is not None:
            shape = to_shape(alert.alert_area)
            centroid_lon = shape.centroid.x
            centroid_lat = shape.centroid.y
            if hasattr(shape, "exterior") and shape.exterior:
                poly_coords = [[p[0], p[1]] for p in shape.exterior.coords]
    except Exception:
        pass

    if not poly_coords:
        poly_coords = create_polygon_coords(centroid_lat, centroid_lon, 35.0)

    iss_time = alert.issue_time.isoformat() if alert.issue_time else None
    val_until = alert.valid_until.isoformat() if alert.valid_until else None

    return {
        "id": str(alert.id),
        "nowcast_id": str(alert.nowcast_id),
        "title": f"{alert.severity.capitalize()} {alert.alert_type}",
        "description": alert.message,
        "message": alert.message,
        "alert_type": alert.alert_type,
        "eventType": alert.alert_type,
        "severity": alert.severity.lower(),
        "riskLevel": alert.severity.lower(),
        "issue_time": iss_time,
        "issuedAt": iss_time,
        "valid_until": val_until,
        "validUntil": val_until,
        "centroid_lat": centroid_lat,
        "centroid_lon": centroid_lon,
        "latitude": centroid_lat,
        "longitude": centroid_lon,
        "radius_km": 35.0,
        "polygon": poly_coords,
    }


@router.get("/")
@router.get("/active")
async def get_active_alerts(db: AsyncSession = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    try:
        stmt = (
            select(Alert)
            .where(Alert.valid_until > now)
            .order_by(Alert.issue_time.desc())
        )
        result = await db.execute(stmt)
        alerts = result.scalars().all()
    except Exception:
        alerts = []

    if not alerts:
        live = run_nowcast()
        live_alerts = generate_alerts(live)
        return {
            "alerts": live_alerts,
            "count": len(live_alerts),
        }

    return {
        "alerts": [serialize_alert(a) for a in alerts],
        "count": len(alerts),
    }


@router.get("/{alert_id}")
async def get_alert_by_id(alert_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        stmt = select(Alert).where(Alert.id == alert_id)
        result = await db.execute(stmt)
        alert = result.scalars().first()
    except Exception:
        alert = None

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return serialize_alert(alert)
