"""GET /health -- liveness + DB readiness check."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)) -> dict:
    """Returns API status, database connectivity, and ML model status."""
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"

    from app.services.nowcast_adapter import _get_mode
    try:
        from ml.inference import is_checkpoint_loaded
        checkpoint_loaded = is_checkpoint_loaded()
    except Exception:
        checkpoint_loaded = False

    return {
        "status": "ok",
        "db": db_status,
        "service": "stormsight-ps072",
        "model_mode": _get_mode(),
        "checkpoint_loaded": checkpoint_loaded,
        "pilot_domain": "Delhi NCR (28.61°N, 77.21°E)",
    }
