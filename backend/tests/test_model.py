import numpy as np
import pytest
import torch

from ml.src.model import UNetConvLSTM
from ml.src.baselines import PersistenceNowcaster, OpticalFlowNowcaster


def test_unet_convlstm_architecture():
    model = UNetConvLSTM(
        in_channels=14,
        out_channels=3,
        hidden_channels=32,
        t_in=4,
        t_out=8,
    )
    # [Batch, Time_in, Channels, Height, Width]
    x = torch.randn(1, 4, 14, 64, 64)
    out = model(x)

    # Expected output: [Batch, Time_out=8, Out_Channels=3, Height=64, Width=64]
    assert out.shape == (1, 8, 3, 64, 64)
    # Channel 0 (radar reflectivity) and Channel 1 (occurrence prob) are in [0, 1]
    assert out[:, :, 0].min() >= 0.0
    assert out[:, :, 0].max() <= 1.0
    assert out[:, :, 1].min() >= 0.0
    assert out[:, :, 1].max() <= 1.0


def test_unet_convlstm_backward_compatibility():
    # Model should gracefully handle 7 input channels by padding
    model = UNetConvLSTM(
        in_channels=14,
        out_channels=2,
        hidden_channels=32,
        t_in=4,
        t_out=8,
    )
    x = torch.randn(1, 4, 7, 64, 64)
    out = model(x)
    assert out.shape == (1, 8, 2, 64, 64)


def test_persistence_baseline():
    baseline = PersistenceNowcaster(t_out=8)

    # 3D input [T, H, W]
    radar_seq = np.ones((4, 32, 32), dtype=np.float32) * 0.5
    pred = baseline.predict(radar_seq)
    assert pred.shape == (8, 32, 32)
    assert np.allclose(pred, 0.5)

    # 5D PyTorch input [B, T, C, H, W]
    tensor_input = torch.ones(2, 4, 1, 32, 32) * 0.75
    tensor_pred = baseline.predict(tensor_input)
    assert isinstance(tensor_pred, torch.Tensor)
    assert tensor_pred.shape == (2, 8, 1, 32, 32)
    assert torch.allclose(tensor_pred, torch.tensor(0.75))


def test_optical_flow_baseline():
    baseline = OpticalFlowNowcaster(t_out=8)

    # Synthetic radar field moving eastward
    frame1 = np.zeros((64, 64), dtype=np.float32)
    frame1[20:30, 20:30] = 0.8 # storm core

    frame2 = np.zeros((64, 64), dtype=np.float32)
    frame2[20:30, 24:34] = 0.8 # shifted 4 pixels right

    seq = np.stack([frame1, frame2], axis=0) # [T=2, H=64, W=64]
    pred = baseline.predict(seq)

    assert pred.shape == (8, 64, 64)
    # Check that advected field has positive values and decays over lead times
    assert pred[0].max() > 0.0
    assert pred[-1].max() <= pred[0].max()

    # 5D tensor input [B=1, T=2, C=1, H=64, W=64]
    seq_5d = torch.from_numpy(np.expand_dims(np.expand_dims(seq, axis=0), axis=2))
    pred_5d = baseline.predict(seq_5d)
    assert isinstance(pred_5d, torch.Tensor)
    assert pred_5d.shape == (1, 8, 3, 64, 64)
