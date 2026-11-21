import os
from typing import Any, Tuple
import numpy as np
from scipy.ndimage import zoom

from app.core.config import get_settings

settings = get_settings()


class RadarProcessor:
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

    def process(self, raw_data: Any = None) -> Tuple[np.ndarray, np.ndarray]:
        h, w = self.target_h, self.target_w

        if raw_data is None:
            return np.zeros((h, w), dtype=np.float32), np.zeros((h, w), dtype=np.float32)

        if isinstance(raw_data, str) and os.path.exists(raw_data):
            try:
                if raw_data.endswith(".npy"):
                    arr = np.load(raw_data)
                    return self._clean_and_regrid(arr)
                elif raw_data.endswith((".h5", ".hdf5", ".nc")):
                    return self._load_hdf5_or_netcdf(raw_data)
            except Exception:
                pass

        if isinstance(raw_data, np.ndarray):
            return self._clean_and_regrid(raw_data)

        return np.zeros((h, w), dtype=np.float32), np.zeros((h, w), dtype=np.float32)

    def _load_hdf5_or_netcdf(self, filepath: str) -> Tuple[np.ndarray, np.ndarray]:
        try:
            import h5py
            with h5py.File(filepath, "r") as f:
                for candidate in ["reflectivity", "max_dbz", "MAX_REF", "REF", "dbz"]:
                    if candidate in f:
                        data = np.array(f[candidate], dtype=np.float32)
                        return self._clean_and_regrid(data)
        except Exception:
            pass

        try:
            import xarray as xr
            ds = xr.open_dataset(filepath)
            for candidate in ["reflectivity", "max_dbz", "MAX_REF", "REF", "dbz"]:
                if candidate in ds:
                    data = ds[candidate].values.astype(np.float32)
                    return self._clean_and_regrid(data)
        except Exception:
            pass

        return np.zeros((self.target_h, self.target_w), dtype=np.float32), np.zeros((self.target_h, self.target_w), dtype=np.float32)

    def _clean_and_regrid(self, arr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        arr = arr.astype(np.float32)
        valid_mask = (~np.isnan(arr) & (arr >= 0.0)).astype(np.float32)
        arr = np.nan_to_num(arr, nan=0.0, posinf=75.0, neginf=0.0)
        arr = np.clip(arr, 0.0, 75.0)

        if arr.max() > 1.0:
            arr = arr / 70.0
            arr = np.clip(arr, 0.0, 1.0)

        while arr.ndim > 2:
            arr = arr[0]
            valid_mask = valid_mask[0]

        if arr.shape != (self.target_h, self.target_w):
            zy = self.target_h / max(1, arr.shape[0])
            zx = self.target_w / max(1, arr.shape[1])
            try:
                arr = zoom(arr, (zy, zx), order=1)
                valid_mask = zoom(valid_mask, (zy, zx), order=0)
            except Exception:
                out = np.zeros((self.target_h, self.target_w), dtype=np.float32)
                mask_out = np.zeros((self.target_h, self.target_w), dtype=np.float32)
                min_h = min(self.target_h, arr.shape[0])
                min_w = min(self.target_w, arr.shape[1])
                out[:min_h, :min_w] = arr[:min_h, :min_w]
                mask_out[:min_h, :min_w] = valid_mask[:min_h, :min_w]
                arr, valid_mask = out, mask_out

        valid_mask = np.clip(valid_mask, 0.0, 1.0)
        return arr.astype(np.float32), valid_mask.astype(np.float32)
