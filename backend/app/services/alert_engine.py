from __future__ import annotations
import math
from typing import Any


def create_polygon_coords(center_lat, center_lon, radius_km):
    coords = []
    num_points = 8
    radius_deg = radius_km / 111.0

    for i in range(num_points):
        angle = (2.0 * math.pi * i) / num_points
        dlat = radius_deg * math.cos(angle)
        dlon = radius_deg * math.sin(angle) / max(0.2, math.cos(math.radians(center_lat)))
        coords.append([round(center_lon + dlon, 4), round(center_lat + dlat, 4)])

    coords.append(coords[0])
    return coords


def get_alert_title_and_type(severity, hazards):
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

    for cell in nowcast.get("cells", []):
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

        title, event_type = get_alert_title_and_type(severity, hazards)
        poly_coords = create_polygon_coords(c_lat, c_lon, radius)

        message = (
            f"{title} issued for area around ({c_lat:.2f}, {c_lon:.2f}). "
            f"Probability: {int(prob * 100)}%. Severity: {severity.upper()}."
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
            "cell_id": cell_id,
            "latitude": c_lat,
            "longitude": c_lon,
            "centroid_lat": c_lat,
            "centroid_lon": c_lon,
            "radius_km": radius,
            "probability": prob,
            "hazards": hazards,
            "issuedAt": issued_at,
            "issue_time": issued_at,
            "validUntil": valid_until,
            "valid_until": valid_until,
            "polygon": poly_coords,
        }
        alerts.append(alert)

    return alerts
