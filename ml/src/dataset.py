import os
import math
import numpy as np
import torch
from torch.utils.data import Dataset


class ThunderstormDataset(Dataset):
    def __init__(
        self,
        data_dir=None,
        num_samples=100,
        t_in=4,
        t_out=8,
        channels=7,
        h=512,
        w=512,
    ):
        self.data_dir = data_dir
        self.num_samples = max(1, int(num_samples))
        self.t_in = t_in
        self.t_out = t_out
        self.channels = channels
        self.h = h
        self.w = w

        self.files = []
        if self.data_dir and os.path.exists(self.data_dir):
            for f in sorted(os.listdir(self.data_dir)):
                if f.endswith(".npy") or f.endswith(".npz"):
                    self.files.append(os.path.join(self.data_dir, f))

        if len(self.files) > 0:
            self.num_samples = len(self.files)

    def __len__(self):
        return self.num_samples

    def generate_synthetic_sample(self, index):
        rng = np.random.RandomState(index)

        cx = rng.uniform(self.w * 0.2, self.w * 0.6)
        cy = rng.uniform(self.h * 0.2, self.h * 0.6)
        vx = rng.uniform(3.0, 8.0)
        vy = rng.uniform(-2.0, 4.0)
        intensity = rng.uniform(0.6, 1.0)
        radius = rng.uniform(25.0, 50.0)

        total_t = self.t_in + self.t_out
        all_frames = []

        grid_y, grid_x = np.ogrid[: self.h, : self.w]

        for step in range(total_t):
            curr_cx = cx + vx * step
            curr_cy = cy + vy * step

            dist_sq = (grid_x - curr_cx) ** 2 + (grid_y - curr_cy) ** 2
            cell = np.exp(-dist_sq / (2.0 * (radius**2))) * intensity

            c0_radar = np.clip(cell + rng.normal(0, 0.02, (self.h, self.w)), 0.0, 1.0)
            c1_tir1 = np.clip(1.0 - cell * 0.8 + rng.normal(0, 0.02, (self.h, self.w)), 0.0, 1.0)
            c2_wv = np.clip(1.0 - cell * 0.6 + rng.normal(0, 0.02, (self.h, self.w)), 0.0, 1.0)
            c3_diff = np.clip((c1_tir1 - c2_wv + 1.0) * 0.5, 0.0, 1.0)
            c4_lightning = np.clip((cell > 0.4).astype(np.float32) * cell * 1.2, 0.0, 1.0)
            c5_cape = np.full((self.h, self.w), 0.75, dtype=np.float32)
            c6_cin = np.full((self.h, self.w), 0.15, dtype=np.float32)

            frame = np.stack(
                [c0_radar, c1_tir1, c2_wv, c3_diff, c4_lightning, c5_cape, c6_cin],
                axis=0,
            )
            all_frames.append(frame)

        all_frames = np.stack(all_frames, axis=0)

        x = all_frames[: self.t_in]
        y_radar = all_frames[self.t_in :, 0:1, :, :]
        y_lightning = all_frames[self.t_in :, 4:5, :, :]
        y = np.concatenate([y_radar, y_lightning], axis=1)

        x = torch.from_numpy(x).float()
        y = torch.from_numpy(y).float()

        x = torch.nan_to_num(x, nan=0.0, posinf=1.0, neginf=0.0)
        y = torch.nan_to_num(y, nan=0.0, posinf=1.0, neginf=0.0)

        return x, y

    def __getitem__(self, index):
        if len(self.files) == 0:
            return self.generate_synthetic_sample(index)

        path = self.files[index]
        try:
            data = np.load(path)
            if isinstance(data, np.lib.npyio.NpzFile):
                x = data["x"]
                y = data["y"]
            else:
                x = data[: self.t_in]
                y = data[self.t_in : self.t_in + self.t_out, :2]

            x = torch.from_numpy(x).float()
            y = torch.from_numpy(y).float()

            x = torch.nan_to_num(x, nan=0.0, posinf=1.0, neginf=0.0)
            y = torch.nan_to_num(y, nan=0.0, posinf=1.0, neginf=0.0)

            return x, y
        except Exception:
            return self.generate_synthetic_sample(index)
