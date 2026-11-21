from datetime import datetime, timezone
import os
import json
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch

from app.core.config import get_settings
from app.ingestion.radar.processor import RadarProcessor
from app.ingestion.satellite.processor import SatelliteProcessor
from app.ingestion.lightning.processor import LightningProcessor
from app.ingestion.nwp.processor import NWPProcessor

settings = get_settings()


class MultimodalFusedPipeline:
    def __init__(
        self,
        target_h: int = 512,
        target_w: int = 512,
        history_steps: int = 4,
        device: str = "cpu",
    ):
        self.target_h = target_h
        self.target_w = target_w
        self.history_steps = history_steps
        self.device = device

        self.radar_proc = RadarProcessor(target_h=target_h, target_w=target_w)
        self.sat_proc = SatelliteProcessor(target_h=target_h, target_w=target_w)
        self.lgt_proc = LightningProcessor(target_h=target_h, target_w=target_w)
        self.nwp_proc = NWPProcessor(target_h=target_h, target_w=target_w)

    def process_frame(
        self,
        radar_raw: Any = None,
        satellite_raw: Any = None,
        lightning_strokes: Optional[List[dict]] = None,
        nwp_raw: Any = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        # 1. Radar
        radar_grid, radar_mask = self.radar_proc.process(radar_raw)

        # 2. Satellite
        if isinstance(satellite_raw, str):
            sat_dict = self.sat_proc.process(file_path=satellite_raw)
        elif isinstance(satellite_raw, dict):
            sat_dict = self.sat_proc.process(
                tir1=satellite_raw.get("tir1"),
                tir2=satellite_raw.get("tir2"),
                wv=satellite_raw.get("wv"),
            )
        else:
            sat_dict = self.sat_proc.process()
        tir1_grid = sat_dict["tir1"]
        wv_grid = sat_dict["wv"]
        diff_grid = sat_dict["diff"]
        sat_mask = sat_dict["mask"]

        # 3. Lightning
        lgt_grid, lgt_mask = self.lgt_proc.process(lightning_strokes)

        # 4. NWP
        if isinstance(nwp_raw, str):
            nwp_dict = self.nwp_proc.process(file_path=nwp_raw)
        elif isinstance(nwp_raw, dict):
            nwp_dict = self.nwp_proc.process(
                cape=nwp_raw.get("cape"),
                cin=nwp_raw.get("cin"),
            )
        else:
            nwp_dict = self.nwp_proc.process()
        cape_grid = nwp_dict["cape"]
        cin_grid = nwp_dict["cin"]
        nwp_mask = nwp_dict["mask"]

        # 14-channel unified array [14, H, W]
        # Channels 0-6: Normalized features
        # Channels 7-13: Validity masks
        channels = [
            radar_grid,
            tir1_grid,
            wv_grid,
            diff_grid,
            lgt_grid,
            cape_grid,
            cin_grid,
            radar_mask,
            sat_mask,
            sat_mask,
            sat_mask,
            lgt_mask,
            nwp_mask,
            nwp_mask,
        ]
        stacked = np.stack(channels, axis=0).astype(np.float32)

        provenance = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": settings.pilot_domain_name,
            "center": [settings.pilot_center_lat, settings.pilot_center_lon],
            "channels": 14,
            "feature_channels": 7,
            "mask_channels": 7,
            "modalities_present": {
                "radar": bool(radar_mask.mean() > 0.1),
                "satellite": bool(sat_mask.mean() > 0.1),
                "lightning": bool(lgt_mask.mean() > 0.1 and lgt_grid.sum() > 0),
                "nwp": bool(nwp_mask.mean() > 0.1),
            },
        }

        return stacked, provenance

    def build_sequence_tensor(
        self,
        frame_list: List[np.ndarray],
    ) -> torch.Tensor:
        if not frame_list:
            zeros = np.zeros((1, self.history_steps, 14, self.target_h, self.target_w), dtype=np.float32)
            return torch.from_numpy(zeros).to(self.device)

        if len(frame_list) < self.history_steps:
            last = frame_list[-1]
            diff = self.history_steps - len(frame_list)
            frame_list = frame_list + [last] * diff
        elif len(frame_list) > self.history_steps:
            frame_list = frame_list[-self.history_steps:]

        seq = np.stack(frame_list, axis=0) # [T, 14, H, W]
        seq = np.expand_dims(seq, axis=0)  # [1, T, 14, H, W]
        return torch.from_numpy(seq).to(self.device)
