import numpy as np
import torch
from typing import Union


class PersistenceNowcaster:
    def __init__(self, t_out: int = 8):
        self.t_out = t_out

    def predict(self, input_data: Union[np.ndarray, torch.Tensor]) -> Union[np.ndarray, torch.Tensor]:
        is_torch = isinstance(input_data, torch.Tensor)
        if is_torch:
            arr = input_data.detach().cpu().numpy()
        else:
            arr = np.array(input_data)

        if arr.ndim == 2:
            last_frame = arr
            forecast = np.stack([last_frame] * self.t_out, axis=0)
        elif arr.ndim == 3:
            last_frame = arr[-1]
            forecast = np.stack([last_frame] * self.t_out, axis=0)
        elif arr.ndim == 4:
            last_frame = arr[-1]
            forecast = np.stack([last_frame] * self.t_out, axis=0)
        elif arr.ndim == 5:
            last_frame = arr[:, -1:, :, :, :]
            forecast = np.concatenate([last_frame] * self.t_out, axis=1)
        else:
            raise ValueError(f"Unsupported array shape: {arr.shape}")

        if is_torch:
            return torch.from_numpy(forecast).to(input_data.device, dtype=input_data.dtype)
        return forecast
