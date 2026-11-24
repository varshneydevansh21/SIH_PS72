import numpy as np
import pytest

from app.services.contouring import ContourExtractor
from app.services.cell_tracking import (
    CellTracker,
    calculate_bearing,
    calculate_haversine_distance_km,
)
from app.services.impact_service import ImpactService
from app.services.alert_engine import generate_alerts, create_polygon_coords


def test_contour_extractor():
    extractor = ContourExtractor(
        lat_min=24.0,
        lat_max=33.2,
        lon_min=72.0,
        lon_max=82.5,
        min_cell_area_km2=16.0,
    )
    grid = np.zeros((128, 128), dtype=np.float32)
    grid[50:70, 50:70] = 52.0

    cells = extractor.extract_storm_contours(grid, thresholds=(35.0, 45.0))
    assert len(cells) > 0

    first_cell = cells[0]
    assert "cell_id" in first_cell
    assert "max_dbz" in first_cell
    assert first_cell["max_dbz"] >= 45.0
    assert first_cell["severity"] in ["high", "severe", "extreme"]

    poly = first_cell["polygon"]
    assert len(poly) >= 4
    assert poly[0] == poly[-1]
    assert 72.0 <= poly[0][0] <= 82.5
    assert 24.0 <= poly[0][1] <= 33.2


def test_cell_tracking_and_projection():
    tracker = CellTracker()
    center_lat = 28.6139
    center_lon = 77.2090
    speed_kmh = 40.0
    bearing_deg = 270.0
    base_prob = 0.85

    positions = tracker.project_cell_positions(
        center_lat=center_lat,
        center_lon=center_lon,
        speed_kmh=speed_kmh,
        bearing_deg=bearing_deg,
        base_probability=base_prob,
    )

    assert len(positions) == 8
    first = positions[0]
    assert first["minutes_ahead"] == 15
    assert first["lat"] == pytest.approx(center_lat, abs=0.05)
    assert first["lon"] < center_lon
    assert first["distance_traveled_km"] == pytest.approx(10.0, abs=0.5)

    last = positions[-1]
    assert last["minutes_ahead"] == 120
    assert last["distance_traveled_km"] == pytest.approx(80.0, abs=1.0)
    assert last["probability"] < first["probability"]


def test_haversine_and_bearing():
    delhi = (28.6139, 77.2090)
    gurugram = (28.4595, 77.0266)
    dist = calculate_haversine_distance_km(delhi[0], delhi[1], gurugram[0], gurugram[1])
    assert 20.0 <= dist <= 35.0

    bearing = calculate_bearing(delhi[0], delhi[1], gurugram[0], gurugram[1])
    assert 200.0 <= bearing <= 250.0


def test_impact_service():
    impact_svc = ImpactService()
    cell = {
        "cell_id": "TS-001",
        "center": {"lat": 28.55, "lon": 77.15},
        "max_dbz": 54.0,
        "severity": "severe",
        "motion": {"speed_kmh": 40.0, "bearing_deg": 235.0},
    }

    impacts = impact_svc.assess_impacts([cell])
    assert len(impacts) > 0
    first_impact = impacts[0]
    assert "location_name" in first_impact
    assert "eta_minutes" in first_impact
    assert "warning_text" in first_impact
    assert first_impact["eta_minutes"] <= 120


def test_alert_engine_with_real_contours():
    nowcast = {
        "nowcast_id": "nc-test-01",
        "issued_at": "2026-11-22T12:00:00Z",
        "valid_until": "2026-11-22T14:00:00Z",
        "cells": [
            {
                "cell_id": "TS-001",
                "center": {"lat": 28.61, "lon": 77.23},
                "max_dbz": 52.0,
                "severity": "severe",
                "probability": 0.88,
                "motion": {"speed_kmh": 42.0, "bearing_deg": 240.0},
                "polygon": [[77.20, 28.60], [77.25, 28.60], [77.25, 28.65], [77.20, 28.60]],
            }
        ],
    }

    alerts = generate_alerts(nowcast, threshold=0.50)
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert["id"] == "alert-TS-001"
    assert alert["severity"] == "severe"
    assert alert["imd_color"] in ["ORANGE", "RED"]
    assert alert["polygon"] == nowcast["cells"][0]["polygon"]
    assert "impacts" in alert
