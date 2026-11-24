from __future__ import annotations
import math
from typing import Any, Dict, List, Optional
from app.services.impact_service import ImpactService

IMD_COLOR_MAP = {
    "minimal": "GREEN",
    "low": "YELLOW",
    "moderate": "YELLOW",
    "high": "ORANGE",
    "severe": "ORANGE",
    "extreme": "RED",
}


def create_polygon_coords(center_lat: float, center_lon: float, radius_km: float) -> list[list[float]]:
    coords = []
    num_points = 16
    radius_deg = radius_km / 111.0

    for i in range(num_points):
        angle = (2.0 * math.pi * i) / num_points
        dlat = radius_deg * math.cos(angle)
        dlon = radius_deg * math.sin(angle) / max(0.2, math.cos(math.radians(center_lat)))
        coords.append([round(center_lon + dlon, 4), round(center_lat + dlat, 4)])

    coords.append(coords[0])
    return coords


def get_alert_title_and_type(severity: str, hazards: dict) -> tuple[str, str]:
    hail_prob = 0.0
    lightning_prob = 0.0
    wind_kmh = 0

    if isinstance(hazards, dict):
        if "hail" in hazards and isinstance(hazards["hail"], dict):
            hail_prob = hazards["hail"].get("probability", 0.0)
        if "lightning" in hazards and isinstance(hazards["lightning"], dict):
            lightning_prob = hazards["lightning"].get("probability", 0.0)
        wind_kmh = hazards.get("wind_gust_kmh", 0)

    if severity in ["extreme", "severe"] and lightning_prob >= 0.8:
        return "Extreme Lightning Warning", "EXTREME_LIGHTNING"
    if hail_prob >= 0.6:
        return "Severe Hailstorm Warning", "HAILSTORM"
    if wind_kmh >= 70:
        return "High Squall Line Alert", "SQUALL"
    if severity in ["extreme", "severe"]:
        return "Severe Thunderstorm Warning", "THUNDERSTORM"
    return "Thunderstorm Advisory", "THUNDERSTORM"


def generate_alerts(nowcast: dict[str, Any], threshold: float = 0.50) -> list[dict[str, Any]]:
    if not isinstance(nowcast, dict):
        return []

    alerts: list[dict[str, Any]] = []
    issued_at = nowcast.get("issued_at")
    valid_until = nowcast.get("valid_until")
    cells = nowcast.get("cells", [])

    impact_svc = ImpactService()
    all_impacts = impact_svc.assess_impacts(cells) if cells else []

    impacts_by_cell: Dict[str, List[Dict[str, Any]]] = {}
    for imp in all_impacts:
        cid = imp["cell_id"]
        impacts_by_cell.setdefault(cid, []).append(imp)

    for cell in cells:
        if not isinstance(cell, dict):
            continue

        prob = cell.get("probability", 0.0)
        if prob < threshold:
            continue

        cell_id = cell.get("cell_id", "TS-UNK")
        severity = cell.get("severity", "moderate")
        center = cell.get("center", {"lat": 28.61, "lon": 77.23})
        c_lat = center.get("lat", 28.61)
        c_lon = center.get("lon", 77.23)
        radius = cell.get("radius_km", 30.0)
        hazards = cell.get("hazards", {})
        max_dbz = cell.get("max_dbz", 40.0)

        title, event_type = get_alert_title_and_type(severity, hazards)

        if "polygon" in cell and isinstance(cell["polygon"], list) and len(cell["polygon"]) >= 3:
            poly_coords = cell["polygon"]
        else:
            poly_coords = create_polygon_coords(c_lat, c_lon, radius)

        imd_color = IMD_COLOR_MAP.get(severity, "YELLOW")
        cell_impacts = impacts_by_cell.get(cell_id, [])

        if cell_impacts:
            nearest = cell_impacts[0]
            message = (
                f"{title} ({imd_color} ALERT): Convective cell {cell_id} ({max_dbz} dBZ) "
                f"approaching {nearest['location_name']} in {nearest['eta_minutes']} min. "
                f"Confidence: {int(prob * 100)}%."
            )
        else:
            message = (
                f"{title} ({imd_color} ALERT) issued for domain around ({c_lat:.2f}, {c_lon:.2f}). "
                f"Reflectivity: {max_dbz} dBZ. Probability: {int(prob * 100)}%."
            )

        alert = {
            "id": f"alert-{cell_id}",
            "nowcast_id": nowcast.get("nowcast_id", ""),
            "title": title,
            "description": message,
            "message": message,
            "alert_type": event_type,
            "eventType": event_type,
            "severity": severity,
            "riskLevel": severity,
            "imd_color": imd_color,
            "cell_id": cell_id,
            "latitude": c_lat,
            "longitude": c_lon,
            "centroid_lat": c_lat,
            "centroid_lon": c_lon,
            "radius_km": radius,
            "probability": prob,
            "max_dbz": max_dbz,
            "hazards": hazards,
            "impacts": cell_impacts[:3],
            "issuedAt": issued_at,
            "issue_time": issued_at,
            "validUntil": valid_until,
            "valid_until": valid_until,
            "polygon": poly_coords,
        }
        alerts.append(alert)

    return alerts
