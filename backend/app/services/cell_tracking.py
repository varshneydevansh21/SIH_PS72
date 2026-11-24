import math
from typing import Any, Dict, List, Optional, Tuple


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360.0) % 360.0
    return round(bearing, 1)


def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_earth = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


class CellTracker:
    def __init__(self, timesteps: List[int] = None):
        self.timesteps = timesteps or [15, 30, 45, 60, 75, 90, 105, 120]

    def project_cell_positions(
        self,
        center_lat: float,
        center_lon: float,
        speed_kmh: float,
        bearing_deg: float,
        base_probability: float,
    ) -> List[Dict[str, Any]]:
        future_positions = []
        rad_bearing = math.radians(bearing_deg)

        for step_idx, minutes in enumerate(self.timesteps):
            dist_km = speed_kmh * (minutes / 60.0)
            delta_lat = (dist_km * math.cos(rad_bearing)) / 111.0
            cos_lat = max(0.2, math.cos(math.radians(center_lat)))
            delta_lon = (dist_km * math.sin(rad_bearing)) / (111.0 * cos_lat)

            decay = max(0.20, 1.0 - (step_idx * 0.08))
            p_step = round(min(0.99, max(0.10, base_probability * decay)), 2)

            future_positions.append({
                "minutes_ahead": minutes,
                "lat": round(center_lat + delta_lat, 4),
                "lon": round(center_lon + delta_lon, 4),
                "probability": p_step,
                "distance_traveled_km": round(dist_km, 1),
            })

        return future_positions

    def track_and_enrich_cells(
        self,
        cells: List[Dict[str, Any]],
        default_speed_kmh: float = 38.0,
        default_bearing_deg: float = 240.0,
    ) -> List[Dict[str, Any]]:
        enriched = []
        for cell in cells:
            c = cell.get("center", {})
            lat = c.get("lat", 28.61)
            lon = c.get("lon", 77.23)
            max_dbz = cell.get("max_dbz", 40.0)
            base_prob = min(0.98, max(0.35, max_dbz / 65.0))

            speed = cell.get("speed_kmh", default_speed_kmh)
            bearing = cell.get("bearing_deg", default_bearing_deg)

            positions = self.project_cell_positions(
                center_lat=lat,
                center_lon=lon,
                speed_kmh=speed,
                bearing_deg=bearing,
                base_probability=base_prob,
            )

            cell_copy = dict(cell)
            cell_copy["probability"] = round(base_prob, 2)
            cell_copy["motion"] = {
                "bearing_deg": bearing,
                "speed_kmh": speed,
            }
            cell_copy["forecast_positions"] = positions
            cell_copy["hazards"] = {
                "lightning": {
                    "probability": min(0.99, round(base_prob * 1.05, 2)),
                    "flash_rate_per_min": max(1, int(base_prob * 18)),
                },
                "hail": {
                    "probability": round(max(0.05, base_prob - 0.35), 2),
                    "max_diameter_mm": max(5, int(max_dbz * 0.5)),
                },
                "wind_gust_kmh": int(speed * 1.4 + max_dbz * 0.35),
            }
            enriched.append(cell_copy)

        return enriched
