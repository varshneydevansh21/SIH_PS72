import os
from typing import Any, Dict, Optional
import numpy as np
from scipy.ndimage import zoom

from app.core.config import get_settings

settings = get_settings()


class NWPProcessor:
    def __init__(self, target_h: int = 512, target_w: int = 512):
        self.target_h = target_h
        self.target_w = target_w

    def process(
        self,
        cape: Any = None,
        cin: Any = None,
        file_path: Optional[str] = None,
    ) -> Dict[str, np.ndarray]:
        if file_path and os.path.exists(file_path):
            extracted = self._extract_from_file(file_path)
            if extracted:
                cape = extracted.get("cape", cape)
                cin = extracted.get("cin", cin)

        has_obs = cape is not None or cin is not None
        mask_val = 1.0 if has_obs else 0.0

        c_arr = self._clean_field(cape, default_val=1500.0)
        cin_arr = self._clean_field(cin, default_val=80.0)

        cape_norm = np.clip(c_arr / 4000.0, 0.0, 1.0)
        cin_norm = np.clip(cin_arr / 500.0, 0.0, 1.0)
        valid_mask = np.full((self.target_h, self.target_w), mask_val, dtype=np.float32)

        return {
            "cape": cape_norm.astype(np.float32),
            "cin": cin_norm.astype(np.float32),
            "mask": valid_mask,
        }

    def _extract_from_file(self, filepath: str) -> Dict[str, np.ndarray]:
        res = {}
        try:
            import xarray as xr
            ds = xr.open_dataset(filepath)
            for var in ds.data_vars:
                v_lower = str(var).lower()
                if "cape" in v_lower:
                    res["cape"] = ds[var].values.astype(np.float32)
                elif "cin" in v_lower:
                    res["cin"] = ds[var].values.astype(np.float32)
        except Exception:
            pass

        return res

    def _clean_field(self, arr: Any, default_val: float = 0.0) -> np.ndarray:
        if arr is None:
            return np.full((self.target_h, self.target_w), default_val, dtype=np.float32)

        if isinstance(arr, (int, float, np.floating, np.integer)):
            return np.full((self.target_h, self.target_w), float(arr), dtype=np.float32)

        if isinstance(arr, list):
            arr = np.array(arr, dtype=np.float32)

        arr = np.nan_to_num(arr, nan=default_val, posinf=default_val, neginf=0.0)

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
