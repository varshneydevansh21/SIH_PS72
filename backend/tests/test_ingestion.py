import os
import numpy as np
import pytest
import torch

from app.ingestion.downloader import AtmosphericDownloader
from app.ingestion.radar.processor import RadarProcessor
from app.ingestion.satellite.processor import SatelliteProcessor
from app.ingestion.lightning.processor import LightningProcessor
from app.ingestion.nwp.processor import NWPProcessor
from app.ingestion.fused_pipeline import MultimodalFusedPipeline


def test_radar_processor():
    proc = RadarProcessor(target_h=128, target_w=128)

    grid_empty, mask_empty = proc.process(None)
    assert grid_empty.shape == (128, 128)
    assert mask_empty.shape == (128, 128)
    assert grid_empty.max() == 0.0
    assert mask_empty.max() == 0.0

    raw = np.full((64, 64), 35.0, dtype=np.float32)
    grid, mask = proc.process(raw)
    assert grid.shape == (128, 128)
    assert mask.shape == (128, 128)
    assert np.isclose(grid.mean(), 35.0 / 70.0, atol=0.05)
    assert mask.min() == 1.0


def test_satellite_processor():
    proc = SatelliteProcessor(target_h=128, target_w=128)
    res = proc.process(tir1=280.0, tir2=275.0, wv=240.0)
    assert "tir1" in res
    assert "wv" in res
    assert "diff" in res
    assert "mask" in res
    assert res["tir1"].shape == (128, 128)
    assert res["mask"].shape == (128, 128)
    assert 0.0 <= res["tir1"].mean() <= 1.0
    assert 0.0 <= res["diff"].mean() <= 1.0
    assert res["mask"].mean() == 1.0


def test_lightning_processor_vectorized():
    proc = LightningProcessor(
        target_h=128,
        target_w=128,
        lat_min=24.0,
        lat_max=33.2,
        lon_min=72.0,
        lon_max=82.5,
    )
    strokes = [
        {"lat": 28.61, "lon": 77.23, "amplitude_ka": -25},
        {"lat": 28.65, "lon": 77.20, "amplitude_ka": -30},
        {"lat": 28.58, "lon": 77.15, "amplitude_ka": -15},
    ]
    grid, mask = proc.process(strokes, sigma_pixels=2.0)
    assert grid.shape == (128, 128)
    assert mask.shape == (128, 128)
    assert grid.max() > 0.0
    assert grid.max() <= 1.0
    assert mask.min() == 1.0


def test_nwp_processor():
    proc = NWPProcessor(target_h=128, target_w=128)
    res = proc.process(cape=2000.0, cin=50.0)
    assert "cape" in res
    assert "cin" in res
    assert "mask" in res
    assert res["cape"].shape == (128, 128)
    assert np.isclose(res["cape"].mean(), 2000.0 / 4000.0, atol=0.01)
    assert res["mask"].mean() == 1.0


def test_multimodal_fused_pipeline():
    pipeline = MultimodalFusedPipeline(target_h=128, target_w=128, history_steps=4)
    raw_radar = np.full((128, 128), 42.0, dtype=np.float32)
    strokes = [{"lat": 28.61, "lon": 77.23}]

    stacked, provenance = pipeline.process_frame(
        radar_raw=raw_radar,
        satellite_raw={"tir1": 280.0, "wv": 240.0},
        lightning_strokes=strokes,
        nwp_raw={"cape": 2500.0, "cin": 60.0},
    )

    assert stacked.shape == (14, 128, 128)
    assert provenance["channels"] == 14
    assert provenance["feature_channels"] == 7
    assert provenance["mask_channels"] == 7
    assert provenance["modalities_present"]["radar"] is True

    seq_tensor = pipeline.build_sequence_tensor([stacked, stacked])
    assert isinstance(seq_tensor, torch.Tensor)
    assert seq_tensor.shape == (1, 4, 14, 128, 128)


def test_downloader_manifest(tmp_path):
    downloader = AtmosphericDownloader(raw_dir=str(tmp_path))
    assert os.path.exists(downloader.manifest_path)

    test_file = tmp_path / "test.txt"
    test_file.write_text("stormsight_test_data")
    md5 = downloader.compute_md5(str(test_file))
    assert len(md5) == 32

    downloader.log_manifest("TEST_SOURCE", "test.txt", len("stormsight_test_data"), md5, "SUCCESS")
    with open(downloader.manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "TEST_SOURCE" in content
    assert "test.txt" in content
