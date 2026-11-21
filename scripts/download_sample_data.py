import os
import json
import numpy as np


def generate_storm_replay(
    output_dir="data/ground_truth",
    filename="delhi_convective_squall_2024.npz",
    h=512,
    w=512,
    t_in=4,
    t_out=8,
):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("data/raw/radar", exist_ok=True)
    os.makedirs("data/raw/satellite", exist_ok=True)
    os.makedirs("data/raw/lightning", exist_ok=True)
    os.makedirs("data/raw/nwp", exist_ok=True)

    rng = np.random.RandomState(42)
    total_t = t_in + t_out
    frames = []

    grid_y, grid_x = np.ogrid[:h, :w]
    cx = w * 0.35
    cy = h * 0.40
    vx = 7.5
    vy = 2.2
    radius = 45.0

    for step in range(total_t):
        curr_cx = cx + vx * step
        curr_cy = cy + vy * step

        dist_sq = (grid_x - curr_cx) ** 2 + (grid_y - curr_cy) ** 2
        core = np.exp(-dist_sq / (2.0 * (radius**2)))

        c0_radar = np.clip(core * 0.85 + rng.normal(0, 0.015, (h, w)), 0.0, 1.0)
        c1_tir1 = np.clip(1.0 - core * 0.75 + rng.normal(0, 0.015, (h, w)), 0.0, 1.0)
        c2_wv = np.clip(1.0 - core * 0.55 + rng.normal(0, 0.015, (h, w)), 0.0, 1.0)
        c3_diff = np.clip((c1_tir1 - c2_wv + 1.0) * 0.5, 0.0, 1.0)
        c4_lightning = np.clip((core > 0.45).astype(np.float32) * core * 1.3, 0.0, 1.0)
        c5_cape = np.full((h, w), 0.82, dtype=np.float32)
        c6_cin = np.full((h, w), 0.12, dtype=np.float32)

        f = np.stack(
            [c0_radar, c1_tir1, c2_wv, c3_diff, c4_lightning, c5_cape, c6_cin],
            axis=0,
        )
        frames.append(f)

    all_data = np.stack(frames, axis=0)
    x = all_data[:t_in].astype(np.float32)
    y_radar = all_data[t_in:, 0:1, :, :]
    y_lightning = all_data[t_in:, 4:5, :, :]
    y = np.concatenate([y_radar, y_lightning], axis=1).astype(np.float32)

    save_path = os.path.join(output_dir, filename)
    np.savez_compressed(save_path, x=x, y=y)

    metadata = {
        "event_id": "IN-2024-DEL-SQUALL",
        "description": "Pre-monsoon convective squall line across Delhi-NCR",
        "center": {"lat": 28.6139, "lon": 77.2090},
        "spatial_resolution_km": 2.0,
        "grid_shape": [h, w],
        "input_timesteps": t_in,
        "forecast_timesteps": t_out,
        "time_interval_minutes": 15,
        "file": save_path,
        "channels": [
            "radar_reflectivity",
            "satellite_tir1",
            "satellite_wv",
            "tir1_wv_diff",
            "lightning_density",
            "nwp_cape",
            "nwp_cin",
        ],
    }

    meta_path = os.path.join(output_dir, "event_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return save_path


if __name__ == "__main__":
    generate_storm_replay()
