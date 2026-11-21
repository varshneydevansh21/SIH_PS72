import torch
import torch.nn.functional as F
import numpy as np


def to_tensor(data, device="cpu"):
    if data is None:
        return None
    if isinstance(data, np.ndarray):
        data = torch.from_numpy(data)
    elif not isinstance(data, torch.Tensor):
        data = torch.tensor(data)
    data = data.float()
    data = torch.nan_to_num(data, nan=0.0, posinf=1.0, neginf=0.0)
    return data.to(device)


def match_shape(tensor, target_b, target_t, target_h, target_w, device="cpu"):
    if tensor is None:
        return torch.zeros((target_b, target_t, 1, target_h, target_w), dtype=torch.float32, device=device)

    if tensor.dim() == 2:
        tensor = tensor.unsqueeze(0).unsqueeze(0).unsqueeze(0)
    elif tensor.dim() == 3:
        if tensor.shape[0] == target_t:
            tensor = tensor.unsqueeze(0).unsqueeze(2)
        else:
            tensor = tensor.unsqueeze(1).unsqueeze(1)
    elif tensor.dim() == 4:
        if tensor.shape[1] == target_t:
            tensor = tensor.unsqueeze(2)
        elif tensor.shape[0] == target_b and tensor.shape[1] == 1:
            tensor = tensor.unsqueeze(1)
        else:
            tensor = tensor.unsqueeze(1)
    elif tensor.dim() == 5:
        if tensor.shape[2] != 1:
            tensor = tensor[:, :, :1, :, :]
    else:
        return torch.zeros((target_b, target_t, 1, target_h, target_w), dtype=torch.float32, device=device)

    curr_b, curr_t, curr_c, curr_h, curr_w = tensor.shape

    if curr_t < target_t:
        last_frame = tensor[:, -1:, :, :, :]
        repeats = target_t - curr_t
        tensor = torch.cat([tensor] + [last_frame] * repeats, dim=1)
    elif curr_t > target_t:
        tensor = tensor[:, -target_t:, :, :, :]

    if curr_b < target_b:
        tensor = tensor.repeat(target_b, 1, 1, 1, 1)
    elif curr_b > target_b:
        tensor = tensor[:target_b]

    curr_b, curr_t, curr_c, curr_h, curr_w = tensor.shape
    if curr_h != target_h or curr_w != target_w:
        reshaped = tensor.view(curr_b * curr_t, curr_c, curr_h, curr_w)
        resized = F.interpolate(reshaped, size=(target_h, target_w), mode="bilinear", align_corners=False)
        tensor = resized.view(curr_b, curr_t, curr_c, target_h, target_w)

    return tensor.to(device)


class TensorFusion:
    def __init__(self, target_h=512, target_w=512, target_t=4, device="cpu"):
        self.target_h = target_h
        self.target_w = target_w
        self.target_t = target_t
        self.device = device

    def normalize_channel(self, tensor, min_val, max_val):
        if tensor is None:
            return None
        tensor = torch.clamp(tensor, min=min_val, max=max_val)
        denom = max_val - min_val
        if denom == 0:
            return torch.zeros_like(tensor)
        return (tensor - min_val) / denom

    def fuse(
        self,
        radar=None,
        satellite_tir1=None,
        satellite_wv=None,
        satellite_diff=None,
        lightning=None,
        nwp_cape=None,
        nwp_cin=None,
        batch_size=1,
    ):
        dev = self.device
        b = max(1, int(batch_size))
        t = self.target_t
        h = self.target_h
        w = self.target_w

        radar_t = to_tensor(radar, dev)
        sat_tir1_t = to_tensor(satellite_tir1, dev)
        sat_wv_t = to_tensor(satellite_wv, dev)
        sat_diff_t = to_tensor(satellite_diff, dev)
        lightning_t = to_tensor(lightning, dev)
        cape_t = to_tensor(nwp_cape, dev)
        cin_t = to_tensor(nwp_cin, dev)

        if sat_diff_t is None and sat_tir1_t is not None and sat_wv_t is not None:
            if sat_tir1_t.shape == sat_wv_t.shape:
                sat_diff_t = sat_tir1_t - sat_wv_t

        radar_norm = self.normalize_channel(radar_t, 0.0, 70.0)
        sat_tir1_norm = self.normalize_channel(sat_tir1_t, 180.0, 320.0)
        sat_wv_norm = self.normalize_channel(sat_wv_t, 190.0, 280.0)
        sat_diff_norm = self.normalize_channel(sat_diff_t, -30.0, 30.0)

        if lightning_t is not None and lightning_t.max() > 1.0:
            lightning_norm = self.normalize_channel(lightning_t, 0.0, 100.0)
        else:
            lightning_norm = lightning_t

        cape_norm = self.normalize_channel(cape_t, 0.0, 5000.0)
        cin_norm = self.normalize_channel(cin_t, 0.0, 500.0)

        c0 = match_shape(radar_norm, b, t, h, w, dev)
        c1 = match_shape(sat_tir1_norm, b, t, h, w, dev)
        c2 = match_shape(sat_wv_norm, b, t, h, w, dev)
        c3 = match_shape(sat_diff_norm, b, t, h, w, dev)
        c4 = match_shape(lightning_norm, b, t, h, w, dev)
        c5 = match_shape(cape_norm, b, t, h, w, dev)
        c6 = match_shape(cin_norm, b, t, h, w, dev)

        fused = torch.cat([c0, c1, c2, c3, c4, c5, c6], dim=2)
        fused = torch.nan_to_num(fused, nan=0.0, posinf=1.0, neginf=0.0)
        return torch.clamp(fused, 0.0, 1.0)
