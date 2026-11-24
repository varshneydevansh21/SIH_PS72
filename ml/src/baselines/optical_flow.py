import numpy as np
import cv2
import torch
from typing import Union, Tuple, Optional


class OpticalFlowNowcaster:
    def __init__(
        self,
        t_out: int = 8,
        decay_factor: float = 0.03,
        pyr_scale: float = 0.5,
        levels: int = 3,
        winsize: int = 15,
        iterations: int = 3,
        poly_n: int = 5,
        poly_sigma: float = 1.2,
    ):
        self.t_out = t_out
        self.decay_factor = decay_factor
        self.pyr_scale = pyr_scale
        self.levels = levels
        self.winsize = winsize
        self.iterations = iterations
        self.poly_n = poly_n
        self.poly_sigma = poly_sigma

    def compute_motion_vectors(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> np.ndarray:
        p8 = (np.clip(prev_frame, 0.0, 1.0) * 255.0).astype(np.uint8)
        c8 = (np.clip(curr_frame, 0.0, 1.0) * 255.0).astype(np.uint8)

        flow = cv2.calcOpticalFlowFarneback(
            p8,
            c8,
            None,
            pyr_scale=self.pyr_scale,
            levels=self.levels,
            winsize=self.winsize,
            iterations=self.iterations,
            poly_n=self.poly_n,
            poly_sigma=self.poly_sigma,
            flags=0,
        )
        return flow

    def advect(self, frame: np.ndarray, flow: np.ndarray, step_multiplier: float = 1.0) -> np.ndarray:
        h, w = frame.shape[:2]
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))

        map_x = (grid_x - flow[..., 0] * step_multiplier).astype(np.float32)
        map_y = (grid_y - flow[..., 1] * step_multiplier).astype(np.float32)

        advected = cv2.remap(
            frame.astype(np.float32),
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0.0,
        )
        return advected

    def predict(
        self,
        sequence: Union[np.ndarray, torch.Tensor],
    ) -> Union[np.ndarray, torch.Tensor]:
        is_torch = isinstance(sequence, torch.Tensor)
        if is_torch:
            arr = sequence.detach().cpu().numpy()
        else:
            arr = np.array(sequence)

        is_5d = (arr.ndim == 5)
        if is_5d:
            b, t, c, h, w = arr.shape
            batch_predictions = []
            for bi in range(b):
                sub_seq = arr[bi] # [T, C, H, W]
                r_prev = sub_seq[-2, 0] if t >= 2 else sub_seq[-1, 0]
                r_curr = sub_seq[-1, 0]
                flow = self.compute_motion_vectors(r_prev, r_curr)

                steps = []
                cur_field = r_curr.copy()
                for step_idx in range(1, self.t_out + 1):
                    advected = self.advect(cur_field, flow, step_multiplier=1.0)
                    decay = np.exp(-self.decay_factor * step_idx)
                    advected = np.clip(advected * decay, 0.0, 1.0)
                    cur_field = advected

                    prob_occurrence = np.clip((advected - (35.0 / 70.0)) / (20.0 / 70.0), 0.0, 1.0)
                    lgt_density = np.clip((advected - (40.0 / 70.0)) / (25.0 / 70.0), 0.0, 1.0)

                    step_frame = np.stack([advected, prob_occurrence, lgt_density], axis=0)
                    steps.append(step_frame)

                batch_predictions.append(np.stack(steps, axis=0))

            res = np.stack(batch_predictions, axis=0) # [B, T_out, 3, H, W]
            if is_torch:
                return torch.from_numpy(res).to(sequence.device, dtype=torch.float32)
            return res

        elif arr.ndim == 3: # [T, H, W]
            t = arr.shape[0]
            r_prev = arr[-2] if t >= 2 else arr[-1]
            r_curr = arr[-1]
            flow = self.compute_motion_vectors(r_prev, r_curr)

            steps = []
            cur_field = r_curr.copy()
            for step_idx in range(1, self.t_out + 1):
                advected = self.advect(cur_field, flow, step_multiplier=1.0)
                decay = np.exp(-self.decay_factor * step_idx)
                advected = np.clip(advected * decay, 0.0, 1.0)
                cur_field = advected
                steps.append(advected)

            res = np.stack(steps, axis=0) # [T_out, H, W]
            if is_torch:
                return torch.from_numpy(res).to(sequence.device, dtype=torch.float32)
            return res

        else:
            raise ValueError(f"Unsupported input dimension for optical flow: {arr.shape}")
