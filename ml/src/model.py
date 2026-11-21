import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.2, inplace=True),
        )

    def forward(self, x):
        return self.conv(x)


class ConvLSTMCell(nn.Module):
    def __init__(self, in_channels, hidden_channels, kernel_size=3):
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        padding = kernel_size // 2
        self.conv = nn.Conv2d(
            in_channels + hidden_channels,
            4 * hidden_channels,
            kernel_size=kernel_size,
            padding=padding,
        )

    def forward(self, x, state=None):
        b, _, h, w = x.shape
        if state is None:
            hidden = torch.zeros(b, self.hidden_channels, h, w, device=x.device, dtype=x.dtype)
            cell = torch.zeros(b, self.hidden_channels, h, w, device=x.device, dtype=x.dtype)
        else:
            hidden, cell = state
            if hidden.shape[0] != b or hidden.shape[2:] != (h, w) or hidden.device != x.device:
                hidden = torch.zeros(b, self.hidden_channels, h, w, device=x.device, dtype=x.dtype)
                cell = torch.zeros(b, self.hidden_channels, h, w, device=x.device, dtype=x.dtype)

        combined = torch.cat([x, hidden], dim=1)
        gates = self.conv(combined)
        i, f, o, g = torch.split(gates, self.hidden_channels, dim=1)

        i = torch.sigmoid(i)
        f = torch.sigmoid(f)
        o = torch.sigmoid(o)
        g = torch.tanh(g)

        c_next = f * cell + i * g
        h_next = o * torch.tanh(c_next)
        return h_next, (h_next, c_next)


class UNetConvLSTM(nn.Module):
    def __init__(
        self,
        in_channels=7,
        out_channels=2,
        hidden_channels=64,
        t_in=4,
        t_out=8,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.hidden_channels = hidden_channels
        self.t_in = t_in
        self.t_out = t_out

        self.enc1 = DoubleConv(in_channels, 32)
        self.pool1 = nn.MaxPool2d(2)

        self.enc2 = DoubleConv(32, 64)
        self.pool2 = nn.MaxPool2d(2)

        self.enc3 = DoubleConv(64, 128)
        self.pool3 = nn.MaxPool2d(2)

        self.bottleneck = DoubleConv(128, hidden_channels)

        self.convlstm = ConvLSTMCell(hidden_channels, hidden_channels, kernel_size=3)

        self.up3 = nn.ConvTranspose2d(hidden_channels, 128, kernel_size=2, stride=2)
        self.dec3 = DoubleConv(128 + 128, 64)

        self.up2 = nn.ConvTranspose2d(64, 64, kernel_size=2, stride=2)
        self.dec2 = DoubleConv(64 + 64, 32)

        self.up1 = nn.ConvTranspose2d(32, 32, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(32 + 32, 32)

        self.radar_head = nn.Conv2d(32, 1, kernel_size=1)
        self.lightning_head = nn.Conv2d(32, 1, kernel_size=1)

    def forward(self, x):
        if x.dim() == 4:
            x = x.unsqueeze(0)

        if x.dim() != 5:
            raise ValueError("Expected 5D tensor input [B, T, C, H, W]")

        x = torch.nan_to_num(x, nan=0.0, posinf=1.0, neginf=0.0)

        curr_b, curr_t, curr_c, curr_h, curr_w = x.shape

        if curr_c < self.in_channels:
            pad = torch.zeros(
                curr_b,
                curr_t,
                self.in_channels - curr_c,
                curr_h,
                curr_w,
                device=x.device,
                dtype=x.dtype,
            )
            x = torch.cat([x, pad], dim=2)
        elif curr_c > self.in_channels:
            x = x[:, :, : self.in_channels, :, :]

        if curr_t < self.t_in:
            last_frame = x[:, -1:, :, :, :]
            repeats = self.t_in - curr_t
            x = torch.cat([x] + [last_frame] * repeats, dim=1)
        elif curr_t > self.t_in:
            x = x[:, -self.t_in :, :, :, :]

        lstm_state = None
        last_e1 = None
        last_e2 = None
        last_e3 = None
        h = None

        for t in range(self.t_in):
            xt = x[:, t, :, :, :]
            e1 = self.enc1(xt)
            p1 = self.pool1(e1)

            e2 = self.enc2(p1)
            p2 = self.pool2(e2)

            e3 = self.enc3(p2)
            p3 = self.pool3(e3)

            b = self.bottleneck(p3)
            h, lstm_state = self.convlstm(b, lstm_state)

            last_e1 = e1
            last_e2 = e2
            last_e3 = e3

        predictions = []

        for step in range(self.t_out):
            h, lstm_state = self.convlstm(h, lstm_state)

            d3 = self.up3(h)
            if d3.shape[2:] != last_e3.shape[2:]:
                d3 = F.interpolate(
                    d3, size=last_e3.shape[2:], mode="bilinear", align_corners=False
                )
            d3 = self.dec3(torch.cat([d3, last_e3], dim=1))

            d2 = self.up2(d3)
            if d2.shape[2:] != last_e2.shape[2:]:
                d2 = F.interpolate(
                    d2, size=last_e2.shape[2:], mode="bilinear", align_corners=False
                )
            d2 = self.dec2(torch.cat([d2, last_e2], dim=1))

            d1 = self.up1(d2)
            if d1.shape[2:] != last_e1.shape[2:]:
                d1 = F.interpolate(
                    d1, size=last_e1.shape[2:], mode="bilinear", align_corners=False
                )
            d1 = self.dec1(torch.cat([d1, last_e1], dim=1))

            pred_radar = torch.relu(self.radar_head(d1))
            pred_lightning = torch.sigmoid(self.lightning_head(d1))
            pred_step = torch.cat([pred_radar, pred_lightning], dim=1)

            predictions.append(pred_step)

        out = torch.stack(predictions, dim=1)
        return out
