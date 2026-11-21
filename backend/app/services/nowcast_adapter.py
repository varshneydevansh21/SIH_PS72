from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

_NOWCAST_STUB: dict[str, Any] = {
    "nowcast_id": "stub-001",
    "issued_at": "2026-11-20T12:00:00Z",
    "valid_until": "2026-11-20T14:00:00Z",
    "horizon_minutes": 120,
    "interval_minutes": 15,
    "timesteps": [15, 30, 45, 60, 75, 90, 105, 120],
    "cells": [
        {
            "cell_id": "TS-001",
            "center": {"lat": 28.61, "lon": 77.23},
            "radius_km": 35.0,
            "severity": "severe",
            "probability": 0.82,
            "hazards": {
                "lightning": {"probability": 0.88, "flash_rate_per_min": 12},
                "hail": {"probability": 0.45, "max_diameter_mm": 25},
                "wind_gust_kmh": 75,
            },
            "motion": {"bearing_deg": 245, "speed_kmh": 42},
            "forecast_positions": [
                {"minutes_ahead": 15, "lat": 28.58, "lon": 77.18, "probability": 0.80},
                {"minutes_ahead": 30, "lat": 28.55, "lon": 77.13, "probability": 0.74},
                {"minutes_ahead": 60, "lat": 28.49, "lon": 77.03, "probability": 0.61},
                {"minutes_ahead": 120, "lat": 28.37, "lon": 76.83, "probability": 0.43},
            ],
        },
    ],
    "model": {"name": "ps72-nowcast-stub", "version": "0.1.0", "mode": "stub", "checkpoint_loaded": False},
    "data_sources_used": ["radar", "satellite", "lightning"],
}

_MODE: str | None = None


def _detect_mode() -> str:
    try:
        from app.core.config import get_settings
        settings = get_settings()
        if getattr(settings, "ml_force_stub", False):
            return "stub"
    except Exception:
        pass

    try:
        from ml.inference import is_checkpoint_loaded
        return "real" if is_checkpoint_loaded() else "stub"
    except Exception:
        return "stub"


def _get_mode() -> str:
    global _MODE
    if _MODE is None:
        _MODE = _detect_mode()
        if _MODE == "stub":
            logger.warning(
                "[ML ADAPTER] Running in STUB MODE — valid trained checkpoint not loaded or ML_FORCE_STUB=true."
            )
        else:
            logger.info("[ML ADAPTER] Running in REAL MODE — trained checkpoint loaded.")
    return _MODE


def get_stub_nowcast() -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    stub = dict(_NOWCAST_STUB)
    stub["issued_at"] = now.isoformat()
    stub["valid_until"] = (now + timedelta(minutes=120)).isoformat()
    stub["model"] = {
        "name": "ps72-nowcast-stub",
        "version": "0.1.0",
        "mode": "stub",
        "checkpoint_loaded": False,
    }
    return stub


def run_nowcast(
    radar_data: Any | None = None,
    satellite_data: Any | None = None,
    lightning_data: Any | None = None,
    nwp_data: Any | None = None,
    include_demo_cells: bool = False,
) -> dict[str, Any]:
    if _get_mode() == "real":
        try:
            from ml.inference import run_nowcast as _ml_nowcast
            result = _ml_nowcast(
                radar_data=radar_data,
                satellite_data=satellite_data,
                lightning_data=lightning_data,
                nwp_data=nwp_data,
                include_demo_cells=include_demo_cells,
            )
            if isinstance(result, dict) and "cells" in result:
                return result
        except Exception as exc:
            logger.error(f"Inference error: {exc}")

    return get_stub_nowcast()


def reset_mode() -> None:
    global _MODE
    _MODE = None
