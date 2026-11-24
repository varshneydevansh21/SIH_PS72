import math
from typing import Any, Dict, List, Optional
from app.services.cell_tracking import calculate_haversine_distance_km, calculate_bearing

NCR_LOCATIONS = [
    {"name": "New Delhi", "district": "New Delhi", "lat": 28.6139, "lon": 77.2090, "population": 30000000},
    {"name": "Gurugram", "district": "Gurgaon", "lat": 28.4595, "lon": 77.0266, "population": 1500000},
    {"name": "Noida", "district": "Gautam Buddha Nagar", "lat": 28.5355, "lon": 77.3910, "population": 1000000},
    {"name": "Ghaziabad", "district": "Ghaziabad", "lat": 28.6692, "lon": 77.4538, "population": 2300000},
    {"name": "Faridabad", "district": "Faridabad", "lat": 28.4089, "lon": 77.3178, "population": 1400000},
    {"name": "Meerut", "district": "Meerut", "lat": 28.9845, "lon": 77.7064, "population": 1500000},
    {"name": "Sonipat", "district": "Sonipat", "lat": 28.9931, "lon": 77.0151, "population": 400000},
    {"name": "Panipat", "district": "Panipat", "lat": 29.3909, "lon": 76.9635, "population": 450000},
    {"name": "Rohtak", "district": "Rohtak", "lat": 28.8955, "lon": 76.6066, "population": 370000},
    {"name": "Alwar", "district": "Alwar", "lat": 27.5530, "lon": 76.6346, "population": 350000},
    {"name": "Rewari", "district": "Rewari", "lat": 28.1833, "lon": 76.6167, "population": 200000},
    {"name": "Palwal", "district": "Palwal", "lat": 28.1447, "lon": 77.3260, "population": 230000},
    {"name": "Hapur", "district": "Hapur", "lat": 28.7306, "lon": 77.7758, "population": 260000},
]


class ImpactService:
    def __init__(self, target_locations: Optional[List[Dict[str, Any]]] = None):
        self.locations = target_locations or NCR_LOCATIONS

    def assess_impacts(
        self,
        cells: List[Dict[str, Any]],
        max_horizon_minutes: int = 120,
    ) -> List[Dict[str, Any]]:
        impacts = []

        for cell in cells:
            cell_id = cell.get("cell_id", "TS-UNK")
            center = cell.get("center", {})
            c_lat = center.get("lat")
            c_lon = center.get("lon")
            if c_lat is None or c_lon is None:
                continue

            motion = cell.get("motion", {})
            speed = motion.get("speed_kmh", 35.0)
            cell_bearing = motion.get("bearing_deg", 240.0)
            severity = cell.get("severity", "moderate")
            max_dbz = cell.get("max_dbz", 40.0)

            for loc in self.locations:
                loc_lat = loc["lat"]
                loc_lon = loc["lon"]
                dist_km = calculate_haversine_distance_km(c_lat, c_lon, loc_lat, loc_lon)

                bearing_to_city = calculate_bearing(c_lat, c_lon, loc_lat, loc_lon)

                angle_diff = abs(cell_bearing - bearing_to_city)
                if angle_diff > 180.0:
                    angle_diff = 360.0 - angle_diff

                if angle_diff <= 40.0 or dist_km <= 15.0:
                    eta_min = int((dist_km / max(10.0, speed)) * 60.0)
                    if eta_min <= max_horizon_minutes:
                        impacts.append({
                            "cell_id": cell_id,
                            "location_name": loc["name"],
                            "district": loc["district"],
                            "distance_km": round(dist_km, 1),
                            "eta_minutes": max(0, eta_min),
                            "severity": severity,
                            "max_dbz": max_dbz,
                            "cell_bearing": cell_bearing,
                            "warning_text": (
                                f"{severity.capitalize()} thunderstorm ({max_dbz} dBZ) "
                                f"approaching {loc['name']} from {int(cell_bearing)}°. "
                                f"Estimated arrival in {max(0, eta_min)} minutes."
                            ),
                        })

        impacts.sort(key=lambda x: x["eta_minutes"])
        return impacts
