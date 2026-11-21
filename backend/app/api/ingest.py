from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/radar")
async def ingest_radar() -> dict:
    from app.ingestion.radar.processor import RadarProcessor

    processor = RadarProcessor()
    grid, mask = processor.process()
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "status": "success",
        "source": "radar",
        "timestamp": now_iso,
        "grid_shape": list(grid.shape),
        "max_dbz_normalized": float(grid.max()),
        "has_observations": bool(mask.max() > 0),
    }


@router.post("/lightning")
async def ingest_lightning() -> dict:
    from app.ingestion.lightning.processor import LightningProcessor

    processor = LightningProcessor()
    grid, mask = processor.process()
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "status": "success",
        "source": "lightning",
        "timestamp": now_iso,
        "grid_shape": list(grid.shape),
        "has_observations": bool(mask.max() > 0),
    }


@router.post("/satellite")
async def ingest_satellite() -> dict:
    from app.ingestion.satellite.insat_client import INSATClient

    client = INSATClient()
    raw = await client.fetch()
    processed = await client.process(raw)
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "status": "success",
        "source": "satellite",
        "timestamp": now_iso,
        "channels": list(processed.keys()) if isinstance(processed, dict) else [],
    }


@router.post("/nwp")
async def ingest_nwp() -> dict:
    from app.ingestion.nwp.gfs_client import GFSClient

    client = GFSClient()
    raw = await client.fetch()
    processed = await client.process(raw)
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "status": "success",
        "source": "nwp",
        "timestamp": now_iso,
        "variables": list(processed.keys()) if isinstance(processed, dict) else [],
    }
