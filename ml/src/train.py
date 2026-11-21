import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

from ml.src.model import UNetConvLSTM
from ml.src.dataset import ThunderstormDataset


class CombinedNowcastLoss(nn.Module):
    def __init__(self, weight_severe=8.0):
        super().__init__()
        self.weight_severe = weight_severe

    def forward(self, y_pred, y_true):
        y_pred = torch.nan_to_num(y_pred, nan=0.0, posinf=1.0, neginf=0.0)
        y_true = torch.nan_to_num(y_true, nan=0.0, posinf=1.0, neginf=0.0)

        if y_pred.shape != y_true.shape:
            if y_pred.shape[2:] != y_true.shape[2:]:
                y_pred = F.interpolate(
                    y_pred.view(-1, y_pred.shape[2], y_pred.shape[3], y_pred.shape[4]),
                    size=y_true.shape[3:],
                    mode="bilinear",
                    align_corners=False,
                ).view(y_true.shape)

        pred_radar = y_pred[:, :, 0:1, :, :]
        true_radar = y_true[:, :, 0:1, :, :]

        pred_lightning = torch.clamp(y_pred[:, :, 1:2, :, :], 1e-6, 1.0 - 1e-6)
        true_lightning = torch.clamp(y_true[:, :, 1:2, :, :], 0.0, 1.0)

        radar_weight = 1.0 + (self.weight_severe - 1.0) * (true_radar >= 0.5).float()
        radar_mse = torch.mean(radar_weight * ((pred_radar - true_radar) ** 2))

        lightning_weight = 1.0 + 4.0 * (true_lightning >= 0.5).float()
        lightning_bce = F.binary_cross_entropy(
            pred_lightning, true_lightning, weight=lightning_weight
        )

        pred_bin = torch.clamp(pred_radar, 0.0, 1.0)
        true_bin = (true_radar >= 0.5).float()
        hits = torch.sum(pred_bin * true_bin)
        misses = torch.sum((1.0 - pred_bin) * true_bin)
        false_alarms = torch.sum(pred_bin * (1.0 - true_bin))
        soft_csi = (hits + 1e-5) / (hits + misses + false_alarms + 1e-5)
        csi_loss = 1.0 - soft_csi

        total_loss = radar_mse + 2.0 * lightning_bce + 0.5 * csi_loss
        return total_loss


def train_model(
    epochs=5,
    batch_size=2,
    lr=0.0005,
    hidden_channels=64,
    data_dir=None,
    checkpoint_dir="ml/checkpoints",
    device=None,
):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs("model_artifacts/checkpoints", exist_ok=True)

    dataset = ThunderstormDataset(
        data_dir=data_dir,
        num_samples=20,
        t_in=4,
        t_out=8,
        channels=7,
        h=128,
        w=128,
    )
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = UNetConvLSTM(
        in_channels=7,
        out_channels=2,
        hidden_channels=hidden_channels,
        t_in=4,
        t_out=8,
    )
    model.to(device)
    model.train()

    criterion = CombinedNowcastLoss(weight_severe=8.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_loss = float("inf")
    save_path = os.path.join(checkpoint_dir, "model.pt")

    for epoch in range(epochs):
        epoch_loss = 0.0
        num_batches = 0

        for x_batch, y_batch in dataloader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            predictions = model(x_batch)

            loss = criterion(predictions, y_batch)

            if torch.isnan(loss) or torch.isinf(loss):
                continue

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1

        scheduler.step()

        if num_batches > 0:
            avg_loss = epoch_loss / num_batches
            if avg_loss < best_loss:
                best_loss = avg_loss
                torch.save(
                    {
                        "epoch": epoch,
                        "state_dict": model.state_dict(),
                        "model_state_dict": model.state_dict(),
                        "loss": best_loss,
                    },
                    save_path,
                )
                torch.save(
                    model.state_dict(),
                    os.path.join("model_artifacts/checkpoints", "model.pt"),
                )

    return model


if __name__ == "__main__":
    train_model(epochs=2, batch_size=2)
