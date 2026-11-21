import os
from typing import Any, Dict, Optional
import numpy as np

from app.ingestion.base import BaseIngestor
from app.ingestion.satellite.processor import SatelliteProcessor
from app.core.config import get_settings

settings = get_settings()


class INSATClient(BaseIngestor):
    def __init__(self):
        super().__init__(source_name="INSAT_3D_Satellite")
        self.processor = SatelliteProcessor(
            target_h=settings.pilot_grid_h,
            target_w=settings.pilot_grid_w,
        )

    async def fetch(self) -> Any:
        sample_dir = settings.satellite_data_dir
        if os.path.exists(sample_dir):
            files = [
                os.path.join(sample_dir, f)
                for f in sorted(os.listdir(sample_dir))
                if f.endswith((".h5", ".nc", ".npy", ".hdf5"))
            ]
            if files:
                return files[-1]

        return None

    async def process(self, raw_data: Any) -> Dict[str, np.ndarray]:
        if isinstance(raw_data, str) and os.path.exists(raw_data):
            return self.processor.process(file_path=raw_data)
        elif isinstance(raw_data, dict):
            return self.processor.process(
                tir1=raw_data.get("tir1"),
                tir2=raw_data.get("tir2"),
                wv=raw_data.get("wv"),
            )
        return self.processor.process()
