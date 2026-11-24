import cv2
import numpy as np
from typing import Any, Dict, List, Tuple
from shapely.geometry import Polygon, MultiPolygon

from app.core.config import get_settings

settings = get_settings()


class ContourExtractor:
    def __init__(
        self,
        lat_min: float = 24.0,
        lat_max: float = 33.2,
        lon_min: float = 72.0,
        lon_max: float = 82.5,
        min_cell_area_km2: float = 16.0,
    ):
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.min_cell_area_km2 = min_cell_area_km2

    def extract_storm_contours(
        self,
        grid_dbz: np.ndarray,
        thresholds: Tuple[float, ...] = (35.0, 45.0, 55.0),
    ) -> List[Dict[str, Any]]:
        if grid_dbz is None or grid_dbz.size == 0:
            return []

        h, w = grid_dbz.shape[:2]
        pixel_area_km2 = 4.0
        min_pixel_area = max(3.0, self.min_cell_area_km2 / pixel_area_km2)

        extracted_cells = []
        cell_counter = 1

        for thresh in thresholds:
            binary = (grid_dbz >= thresh).astype(np.uint8) * 255
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                area_pixels = cv2.contourArea(cnt)
                if area_pixels < min_pixel_area:
                    continue

                epsilon = 0.015 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)
                if len(approx) < 3:
                    continue

                geo_coords = []
                for pt in approx:
                    px, py = pt[0]
                    lon = self.lon_min + (float(px) / max(1, w - 1)) * (self.lon_max - self.lon_min)
                    lat = self.lat_max - (float(py) / max(1, h - 1)) * (self.lat_max - self.lat_min)
                    geo_coords.append([round(lon, 4), round(lat, 4)])

                if geo_coords[0] != geo_coords[-1]:
                    geo_coords.append(geo_coords[0])

                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    c_px = M["m10"] / M["m00"]
                    c_py = M["m01"] / M["m00"]
                    c_lon = self.lon_min + (c_px / max(1, w - 1)) * (self.lon_max - self.lon_min)
                    c_lat = self.lat_max - (c_py / max(1, h - 1)) * (self.lat_max - self.lat_min)
                else:
                    c_lon = float(np.mean([p[0] for p in geo_coords]))
                    c_lat = float(np.mean([p[1] for p in geo_coords]))

                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(mask, [cnt], -1, 255, -1)
                max_dbz_in_cell = float(grid_dbz[mask == 255].max()) if np.any(mask == 255) else float(thresh)

                area_km2 = round(area_pixels * pixel_area_km2, 1)

                severity = "moderate"
                if max_dbz_in_cell >= 55.0:
                    severity = "extreme"
                elif max_dbz_in_cell >= 45.0:
                    severity = "severe"
                elif max_dbz_in_cell >= 35.0:
                    severity = "high"

                extracted_cells.append({
                    "cell_id": f"TS-{cell_counter:03d}",
                    "threshold_dbz": thresh,
                    "max_dbz": round(max_dbz_in_cell, 1),
                    "area_km2": area_km2,
                    "severity": severity,
                    "center": {"lat": round(c_lat, 4), "lon": round(c_lon, 4)},
                    "polygon": geo_coords,
                })
                cell_counter += 1

        return extracted_cells
