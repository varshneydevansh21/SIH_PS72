from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.shape import to_shape

from app.db.session import get_db
from app.models.nowcast import Nowcast
from app.services.nowcast_adapter import run_nowcast
from app.services.raster_service import RasterService

router = APIRouter(prefix="/nowcast", tags=["nowcast"])
raster_service = RasterService()


def serialize_nowcast(nowcast: Nowcast) -> dict:
    centroid_lat, centroid_lon, radius_km = 20.0, 80.0, 20.0
    try:
        if nowcast.affected_area is not None:
            shape = to_shape(nowcast.affected_area)
            centroid_lon = shape.centroid.x
            centroid_lat = shape.centroid.y
            minx, miny, maxx, maxy = shape.bounds
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
        "radius_km": max(10, radius_km),
    }


@router.get("/")
@router.get("/predict")
@router.get("/latest")
async def get_latest_nowcast(db: AsyncSession = Depends(get_db)) -> dict:
    try:
        stmt = select(Nowcast).order_by(Nowcast.run_time.desc()).limit(10)
        result = await db.execute(stmt)
        nowcasts = result.scalars().all()
    except Exception:
        nowcasts = []

    if not nowcasts:
        live = run_nowcast()
        return {
            "nowcasts": [],
            "cells": live.get("cells", []),
            "issued_at": live.get("issued_at"),
            "valid_until": live.get("valid_until"),
            "model": live.get("model"),
            "count": len(live.get("cells", [])),
        }

    serialized = [serialize_nowcast(n) for n in nowcasts]
    return {
        "nowcasts": serialized,
        "cells": serialized,
        "issued_at": nowcasts[0].run_time.isoformat() if nowcasts[0].run_time else None,
        "model": {"name": "ps72-unet-convlstm", "version": "1.0.0", "source": "database"},
        "count": len(serialized),
    }


@router.get("/raster")
async def get_nowcast_raster(
    minute: int = Query(default=0, ge=0, le=120),
    layer: str = Query(default="composite"),
    width: int = Query(default=256, ge=64, le=1024),
    height: int = Query(default=256, ge=64, le=1024),
) -> Response:
    png_bytes = raster_service.generate_raster_png(
        minute=minute,
        layer=layer,
        width=width,
        height=height,
    )
    return Response(content=png_bytes, media_type="image/png")


@router.get("/{nowcast_id}")
async def get_nowcast_by_id(nowcast_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        stmt = select(Nowcast).where(Nowcast.id == nowcast_id)
        result = await db.execute(stmt)
        nowcast = result.scalars().first()
    except Exception:
        nowcast = None

    if not nowcast:
        raise HTTPException(status_code=404, detail="Nowcast not found")

    return serialize_nowcast(nowcast)


@router.post("/trigger")
async def trigger_nowcast() -> dict:
    result = run_nowcast()
    return {"status": "ok", "nowcast": result}
