import cv2
import numpy as np
from typing import Any, Dict, List, Optional
from app.services.nowcast_adapter import run_nowcast


class RasterService:
    def __init__(
        self,
        lat_min: float = 24.0,
        lat_max: float = 33.2,
        lon_min: float = 72.0,
        lon_max: float = 82.5,
    ):
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max

    def generate_raster_png(
        self,
        minute: int = 0,
        layer: str = "composite",
        width: int = 256,
        height: int = 256,
        nowcast_data: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        if nowcast_data is None:
            nowcast_data = run_nowcast(include_demo_cells=True)

        cells = nowcast_data.get("cells", [])
        grid = np.zeros((height, width), dtype=np.float32)

        decay = max(0.40, 1.0 - (minute / 120.0) * 0.45)

        for cell in cells:
            c = cell.get("center", {})
            lat = c.get("lat", 28.61)
            lon = c.get("lon", 77.23)
            base_dbz = cell.get("max_reflectivity_dbz", cell.get("max_dbz", 45.0))
            rad_km = cell.get("radius_km", 30.0)

            if minute > 0 and "forecast_positions" in cell:
                positions = cell["forecast_positions"]
                match = next((p for p in positions if p.get("minutes_ahead") == minute), None)
                if match:
                    lat = match.get("lat", lat)
                    lon = match.get("lon", lon)
                elif len(positions) > 0:
                    sorted_pos = sorted(positions, key=lambda p: abs(p.get("minutes_ahead", 0) - minute))
                    lat = sorted_pos[0].get("lat", lat)
                    lon = sorted_pos[0].get("lon", lon)

            eff_dbz = base_dbz * decay

            px = int(((lon - self.lon_min) / max(0.001, self.lon_max - self.lon_min)) * (width - 1))
            py = int(((self.lat_max - lat) / max(0.001, self.lat_max - self.lat_min)) * (height - 1))

            km_per_pixel = 2.0
            r_px = max(4, int(rad_km / km_per_pixel))

            y_indices, x_indices = np.ogrid[:height, :width]
            dist_sq = (x_indices - px) ** 2 + (y_indices - py) ** 2
            sigma_sq = max(1.0, (r_px / 2.2) ** 2)

            cell_field = eff_dbz * np.exp(-dist_sq / (2 * sigma_sq))
            grid = np.maximum(grid, cell_field)

        bgra = np.zeros((height, width, 4), dtype=np.uint8)

        if layer in ("lightning",):
            norm_lightning = np.clip(grid / 60.0, 0.0, 1.0)
            mask_active = norm_lightning > 0.15
            bgra[mask_active, 0] = (255 * norm_lightning[mask_active]).astype(np.uint8)
            bgra[mask_active, 1] = (150 * norm_lightning[mask_active]).astype(np.uint8)
            bgra[mask_active, 2] = 240
            bgra[mask_active, 3] = np.clip(norm_lightning[mask_active] * 220, 40, 220).astype(np.uint8)
        else:
            m15 = (grid >= 15.0) & (grid < 25.0)
            bgra[m15] = [231, 233, 4, 130]

            m25 = (grid >= 25.0) & (grid < 35.0)
            bgra[m25] = [244, 159, 1, 155]

            m35 = (grid >= 35.0) & (grid < 45.0)
            bgra[m35] = [1, 197, 1, 185]

            m45 = (grid >= 45.0) & (grid < 55.0)
            bgra[m45] = [2, 248, 253, 215]

            m55 = (grid >= 55.0) & (grid < 62.0)
            bgra[m55] = [0, 109, 255, 230]

            m62 = grid >= 62.0
            bgra[m62] = [0, 0, 253, 245]

        success, encoded = cv2.imencode(".png", bgra)
        if not success:
            return b""
        return encoded.tobytes()
