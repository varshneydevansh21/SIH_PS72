from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Any, Dict, List
import numpy as np
import cv2

router = APIRouter(prefix="/replay", tags=["replay"])

HISTORICAL_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "DEL-2024": {
        "event_id": "DEL-2024",
        "title": "Delhi-NCR Pre-Monsoon Squall Line",
        "date": "2024-05-18T16:30:00Z",
        "radar_station": "DEL (Palam DWR)",
        "center": {"lat": 28.6139, "lon": 77.2090},
        "bounds": {"lat_min": 24.0, "lat_max": 33.2, "lon_min": 72.0, "lon_max": 82.5},
        "peak_dbz": 54.2,
        "total_strikes": 342,
        "lead_time": "120 min",
        "synoptic_summary": "Intense westerly trough triggering severe multicellular convective squall with 75 kmph wind gusts and frequent cloud-to-ground lightning across Delhi-NCR.",
        "metrics": {
            "csi_35dbz": 0.58,
            "csi_45dbz": 0.49,
            "pod": 0.74,
            "far": 0.28,
            "position_rmse_km": 8.2,
            "baseline_skill_lift": "+18.4% vs Farneback Optical Flow",
        },
        "cells": [
            {
                "cell_id": "DEL-CELL-01",
                "center": {"lat": 28.64, "lon": 77.12},
                "radius_km": 36.0,
                "severity": "extreme",
                "probability": 0.92,
                "max_dbz": 54.2,
                "motion": {"bearing_deg": 235.0, "speed_kmh": 46.0},
                "polygon": [
                    [77.02, 28.52],
                    [77.16, 28.48],
                    [77.28, 28.58],
                    [77.26, 28.72],
                    [77.10, 28.76],
                    [77.00, 28.64],
                    [77.02, 28.52],
                ],
                "forecast_positions": [
                    {"minutes_ahead": 15, "lat": 28.58, "lon": 77.04, "probability": 0.90},
                    {"minutes_ahead": 30, "lat": 28.52, "lon": 76.96, "probability": 0.85},
                    {"minutes_ahead": 45, "lat": 28.46, "lon": 76.88, "probability": 0.79},
                    {"minutes_ahead": 60, "lat": 28.40, "lon": 76.80, "probability": 0.72},
                    {"minutes_ahead": 75, "lat": 28.34, "lon": 76.72, "probability": 0.64},
                    {"minutes_ahead": 90, "lat": 28.28, "lon": 76.64, "probability": 0.55},
                    {"minutes_ahead": 105, "lat": 28.22, "lon": 76.56, "probability": 0.48},
                    {"minutes_ahead": 120, "lat": 28.16, "lon": 76.48, "probability": 0.40},
                ],
            },
            {
                "cell_id": "DEL-CELL-02",
                "center": {"lat": 28.45, "lon": 77.40},
                "radius_km": 28.0,
                "severity": "severe",
                "probability": 0.84,
                "max_dbz": 48.0,
                "motion": {"bearing_deg": 240.0, "speed_kmh": 40.0},
                "polygon": [
                    [77.30, 28.38],
                    [77.45, 28.35],
                    [77.52, 28.48],
                    [77.42, 28.55],
                    [77.32, 28.48],
                    [77.30, 28.38],
                ],
                "forecast_positions": [
                    {"minutes_ahead": 15, "lat": 28.40, "lon": 77.33, "probability": 0.82},
                    {"minutes_ahead": 30, "lat": 28.35, "lon": 77.26, "probability": 0.76},
                    {"minutes_ahead": 60, "lat": 28.25, "lon": 77.12, "probability": 0.62},
                    {"minutes_ahead": 120, "lat": 28.05, "lon": 76.84, "probability": 0.38},
                ],
            },
        ],
        "lightning_strokes": [
            {"id": "DEL-LS-1", "lat": 28.62, "lon": 77.14, "type": "CG", "time": "2024-05-18T16:28:12Z"},
            {"id": "DEL-LS-2", "lat": 28.58, "lon": 77.10, "type": "CG", "time": "2024-05-18T16:29:05Z"},
            {"id": "DEL-LS-3", "lat": 28.66, "lon": 77.18, "type": "IC", "time": "2024-05-18T16:29:44Z"},
            {"id": "DEL-LS-4", "lat": 28.44, "lon": 77.38, "type": "CG", "time": "2024-05-18T16:30:00Z"},
        ],
    },
    "KOL-2023": {
        "event_id": "KOL-2023",
        "title": "Kolkata Nor'wester (Kalbaishakhi)",
        "date": "2023-04-22T14:15:00Z",
        "radar_station": "KOL (Kolkata DWR)",
        "center": {"lat": 22.5726, "lon": 88.3639},
        "bounds": {"lat_min": 20.0, "lat_max": 25.5, "lon_min": 85.0, "lon_max": 91.5},
        "peak_dbz": 58.0,
        "total_strikes": 512,
        "lead_time": "120 min",
        "synoptic_summary": "Severe Kalbaishakhi supercell storm with large hailstones (up to 30mm) and severe downdrafts exceeding 85 kmph.",
        "metrics": {
            "csi_35dbz": 0.61,
            "csi_45dbz": 0.52,
            "pod": 0.76,
            "far": 0.25,
            "position_rmse_km": 7.4,
            "baseline_skill_lift": "+21.2% vs Farneback Optical Flow",
        },
        "cells": [
            {
                "cell_id": "KOL-CELL-01",
                "center": {"lat": 22.65, "lon": 88.42},
                "radius_km": 42.0,
                "severity": "extreme",
                "probability": 0.95,
                "max_dbz": 58.0,
                "motion": {"bearing_deg": 135.0, "speed_kmh": 52.0},
                "polygon": [
                    [88.25, 22.55],
                    [88.48, 22.52],
                    [88.58, 22.72],
                    [88.38, 22.80],
                    [88.25, 22.55],
                ],
                "forecast_positions": [
                    {"minutes_ahead": 15, "lat": 22.58, "lon": 88.49, "probability": 0.93},
                    {"minutes_ahead": 30, "lat": 22.51, "lon": 88.56, "probability": 0.88},
                    {"minutes_ahead": 60, "lat": 22.37, "lon": 88.70, "probability": 0.75},
                    {"minutes_ahead": 120, "lat": 22.09, "lon": 88.98, "probability": 0.48},
                ],
            }
        ],
        "lightning_strokes": [
            {"id": "KOL-LS-1", "lat": 22.66, "lon": 88.41, "type": "CG", "time": "2023-04-22T14:12:00Z"},
            {"id": "KOL-LS-2", "lat": 22.62, "lon": 88.46, "type": "CG", "time": "2023-04-22T14:14:10Z"},
        ],
    },
    "MUM-2023": {
        "event_id": "MUM-2023",
        "title": "Mumbai Coastal Convective Band",
        "date": "2023-07-14T08:00:00Z",
        "radar_station": "MUM (Mumbai DWR)",
        "center": {"lat": 19.0760, "lon": 72.8777},
        "bounds": {"lat_min": 17.0, "lat_max": 21.5, "lon_min": 71.0, "lon_max": 75.5},
        "peak_dbz": 51.5,
        "total_strikes": 210,
        "lead_time": "120 min",
        "synoptic_summary": "Offshore convective band propagating inland, causing rapid precipitation rate over 55 mm/hr in Mumbai suburban areas.",
        "metrics": {
            "csi_35dbz": 0.54,
            "csi_45dbz": 0.44,
            "pod": 0.70,
            "far": 0.31,
            "position_rmse_km": 9.1,
            "baseline_skill_lift": "+15.8% vs Farneback Optical Flow",
        },
        "cells": [
            {
                "cell_id": "MUM-CELL-01",
                "center": {"lat": 19.12, "lon": 72.82},
                "radius_km": 30.0,
                "severity": "severe",
                "probability": 0.86,
                "max_dbz": 51.5,
                "motion": {"bearing_deg": 80.0, "speed_kmh": 32.0},
                "polygon": [
                    [72.72, 19.05],
                    [72.90, 19.02],
                    [72.95, 19.20],
                    [72.78, 19.22],
                    [72.72, 19.05],
                ],
                "forecast_positions": [
                    {"minutes_ahead": 15, "lat": 19.13, "lon": 72.89, "probability": 0.84},
                    {"minutes_ahead": 30, "lat": 19.14, "lon": 72.96, "probability": 0.78},
                    {"minutes_ahead": 60, "lat": 19.16, "lon": 73.10, "probability": 0.65},
                    {"minutes_ahead": 120, "lat": 19.20, "lon": 73.38, "probability": 0.42},
                ],
            }
        ],
        "lightning_strokes": [
            {"id": "MUM-LS-1", "lat": 19.10, "lon": 72.84, "type": "CG", "time": "2023-07-14T07:58:30Z"},
        ],
    },
}


@router.get("/events")
async def list_replay_events() -> List[Dict[str, Any]]:
    return [
        {
            "event_id": v["event_id"],
            "title": v["title"],
            "date": v["date"],
            "radar_station": v["radar_station"],
            "center": v["center"],
            "peak_dbz": v["peak_dbz"],
            "total_strikes": v["total_strikes"],
            "lead_time": v["lead_time"],
            "synoptic_summary": v["synoptic_summary"],
            "metrics": v["metrics"],
        }
        for v in HISTORICAL_BENCHMARKS.values()
    ]


@router.get("/events/{event_id}")
async def get_replay_event(event_id: str) -> Dict[str, Any]:
    if event_id not in HISTORICAL_BENCHMARKS:
        raise HTTPException(status_code=404, detail="Replay event not found")
    return HISTORICAL_BENCHMARKS[event_id]


@router.get("/events/{event_id}/raster")
async def get_replay_raster(
    event_id: str,
    minute: int = Query(default=0, ge=0, le=120),
    layer: str = Query(default="composite"),
    width: int = Query(default=256, ge=64, le=512),
    height: int = Query(default=256, ge=64, le=512),
) -> Response:
    if event_id not in HISTORICAL_BENCHMARKS:
        raise HTTPException(status_code=404, detail="Replay event not found")

    event = HISTORICAL_BENCHMARKS[event_id]
    bounds = event["bounds"]
    cells = event["cells"]

    bgra = np.zeros((height, width, 4), dtype=np.uint8)
    decay = max(0.40, 1.0 - (minute / 120.0) * 0.45)

    for cell in cells:
        c = cell["center"]
        lat = c["lat"]
        lon = c["lon"]
        max_dbz = cell["max_dbz"]
        rad_km = cell["radius_km"]

        if minute > 0:
            positions = cell.get("forecast_positions", [])
            match = next((p for p in positions if p["minutes_ahead"] == minute), None)
            if match:
                lat = match["lat"]
                lon = match["lon"]

        eff_dbz = max_dbz * decay

        px = int(((lon - bounds["lon_min"]) / max(0.001, bounds["lon_max"] - bounds["lon_min"])) * (width - 1))
        py = int(((bounds["lat_max"] - lat) / max(0.001, bounds["lat_max"] - bounds["lat_min"])) * (height - 1))

        r_px = max(6, int(rad_km / 2.0))

        y_indices, x_indices = np.ogrid[:height, :width]
        dist_sq = (x_indices - px) ** 2 + (y_indices - py) ** 2
        sigma_sq = max(1.0, (r_px / 2.2) ** 2)

        cell_field = eff_dbz * np.exp(-dist_sq / (2 * sigma_sq))

        m15 = (cell_field >= 15.0) & (cell_field < 25.0)
        bgra[m15] = [231, 233, 4, 130]

        m25 = (cell_field >= 25.0) & (cell_field < 35.0)
        bgra[m25] = [244, 159, 1, 155]

        m35 = (cell_field >= 35.0) & (cell_field < 45.0)
        bgra[m35] = [1, 197, 1, 185]

        m45 = (cell_field >= 45.0) & (cell_field < 55.0)
        bgra[m45] = [2, 248, 253, 215]

        m55 = cell_field >= 55.0
        bgra[m55] = [0, 0, 253, 245]

    success, encoded = cv2.imencode(".png", bgra)
    return Response(content=encoded.tobytes() if success else b"", media_type="image/png")
