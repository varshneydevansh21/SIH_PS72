import os
from typing import Any, Dict, Optional, Tuple
import numpy as np
from scipy.ndimage import zoom

from app.core.config import get_settings

settings = get_settings()


class SatelliteProcessor:
    def __init__(self, target_h: int = 512, target_w: int = 512):
        self.target_h = target_h
        self.target_w = target_w

    def process(
        self,
        tir1: Any = None,
        tir2: Any = None,
        wv: Any = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, np.ndarray]:
        if file_path and os.path.exists(file_path):
            extracted = self._extract_from_file(file_path)
            if extracted:
                tir1 = extracted.get("tir1", tir1)
                tir2 = extracted.get("tir2", tir2)
                wv = extracted.get("wv", wv)

        has_obs = tir1 is not None or wv is not None
        mask_val = 1.0 if has_obs else 0.0

        t1 = self._format_channel(tir1, default_val=280.0)
        t2 = self._format_channel(tir2, default_val=278.0)
        w_ch = self._format_channel(wv, default_val=240.0)

        t1_norm = np.clip((320.0 - t1) / 120.0, 0.0, 1.0)
        w_norm = np.clip((280.0 - w_ch) / 80.0, 0.0, 1.0)

        diff = t1 - t2
        diff_norm = np.clip((diff + 5.0) / 10.0, 0.0, 1.0)

        valid_mask = np.full((self.target_h, self.target_w), mask_val, dtype=np.float32)

        return {
            "tir1": t1_norm.astype(np.float32),
            "wv": w_norm.astype(np.float32),
            "diff": diff_norm.astype(np.float32),
            "mask": valid_mask,
        }

    def _extract_from_file(self, filepath: str) -> Dict[str, np.ndarray]:
        res = {}
        try:
            import h5py
            with h5py.File(filepath, "r") as f:
                for k in f.keys():
                    k_lower = k.lower()
                    if "tir1" in k_lower or "img_tir1" in k_lower:
                        res["tir1"] = np.array(f[k], dtype=np.float32)
                    elif "tir2" in k_lower or "img_tir2" in k_lower:
                        res["tir2"] = np.array(f[k], dtype=np.float32)
                    elif "wv" in k_lower or "img_wv" in k_lower:
                        res["wv"] = np.array(f[k], dtype=np.float32)
        except Exception:
            pass

        if not res:
            try:
                import xarray as xr
                ds = xr.open_dataset(filepath)
                for var in ds.data_vars:
                    v_lower = str(var).lower()
                    if "tir1" in v_lower:
                        res["tir1"] = ds[var].values.astype(np.float32)
                    elif "tir2" in v_lower:
                        res["tir2"] = ds[var].values.astype(np.float32)
                    elif "wv" in v_lower:
                        res["wv"] = ds[var].values.astype(np.float32)
            except Exception:
                pass

        return res

    def _format_channel(self, arr: Any, default_val: float = 250.0) -> np.ndarray:
        if arr is None:
            return np.full((self.target_h, self.target_w), default_val, dtype=np.float32)

        if isinstance(arr, (int, float, np.floating, np.integer)):
            return np.full((self.target_h, self.target_w), float(arr), dtype=np.float32)

        if isinstance(arr, list):
            arr = np.array(arr, dtype=np.float32)

        arr = np.nan_to_num(arr, nan=default_val, posinf=default_val, neginf=default_val)

        if arr.ndim == 0:
            return np.full((self.target_h, self.target_w), float(arr), dtype=np.float32)

        while arr.ndim > 2:
            arr = arr[0]

        if arr.shape != (self.target_h, self.target_w):
            zy = self.target_h / max(1, arr.shape[0])
            zx = self.target_w / max(1, arr.shape[1])
            try:
                arr = zoom(arr, (zy, zx), order=1)
            except Exception:
                out = np.full((self.target_h, self.target_w), default_val, dtype=np.float32)
                min_h = min(self.target_h, arr.shape[0])
                min_w = min(self.target_w, arr.shape[1])
                out[:min_h, :min_w] = arr[:min_h, :min_w]
                arr = out

        return arr.astype(np.float32)
