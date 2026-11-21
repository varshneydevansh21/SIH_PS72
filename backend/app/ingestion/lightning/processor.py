from typing import Any, List, Optional, Tuple
import numpy as np
from scipy.ndimage import gaussian_filter

from app.core.config import get_settings

settings = get_settings()


class LightningProcessor:
    def __init__(
        self,
        target_h: int = 512,
        target_w: int = 512,
        lat_min: float = 24.0,
        lat_max: float = 33.2,
        lon_min: float = 72.0,
        lon_max: float = 82.5,
    ):
        self.target_h = target_h
        self.target_w = target_w
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max

    def process(
        self,
        strokes: Optional[List[dict]] = None,
        sigma_pixels: float = 3.0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        h, w = self.target_h, self.target_w

        if not strokes or not isinstance(strokes, list):
            return np.zeros((h, w), dtype=np.float32), np.zeros((h, w), dtype=np.float32)

        lats = []
        lons = []
        for s in strokes:
            if isinstance(s, dict):
                lat = s.get("lat") or s.get("latitude")
                lon = s.get("lon") or s.get("longitude")
                if lat is not None and lon is not None:
                    if self.lat_min <= lat <= self.lat_max and self.lon_min <= lon <= self.lon_max:
                        lats.append(lat)
                        lons.append(lon)

        if not lats:
            return np.zeros((h, w), dtype=np.float32), np.ones((h, w), dtype=np.float32)

        lat_bins = np.linspace(self.lat_min, self.lat_max, h + 1)
        lon_bins = np.linspace(self.lon_min, self.lon_max, w + 1)

        counts, _, _ = np.histogram2d(lats, lons, bins=[lat_bins, lon_bins])
        counts = np.flipud(counts.astype(np.float32))

        smoothed = gaussian_filter(counts, sigma=sigma_pixels)

        # Standardized log-scale physical normalization (comparable across all frames)
        max_expected_flashes = 50.0
        normalized = np.log1p(smoothed) / np.log1p(max_expected_flashes)
        normalized = np.clip(normalized, 0.0, 1.0).astype(np.float32)
        valid_mask = np.ones((h, w), dtype=np.float32)

        return normalized, valid_mask
