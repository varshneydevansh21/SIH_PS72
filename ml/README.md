# StormSight Machine Learning Engine (PS26072)

## Model Architecture
- **Network**: UNet-ConvLSTM Spatio-Temporal Dual-Head Neural Network
- **Input Tensor**: `[B, T_in=4, C=7, H=512, W=512]`
  - C0: Radar Reflectivity (0 to 70 dBZ, normalized to [0, 1])
  - C1: Satellite TIR1 (Thermal IR 10.8 µm brightness temp)
  - C2: Satellite Water Vapour (6.7 µm)
  - C3: TIR1 - WV Convective Cloud Proxy
  - C4: Lightning Strike Density Heatmap (2D Gaussian KDE)
  - C5: NWP CAPE (Convective Available Potential Energy)
  - C6: NWP CIN (Convective Inhibition)
- **Output Tensor**: `[B, T_out=8, C=2, H=512, W=512]`
  - C0: Predicted Radar Reflectivity (0–120 min ahead, 15-min intervals)
  - C1: Predicted Lightning Strike Probability [0, 1]

## Evaluation Metrics & Operational Targets
- **Target CSI (Critical Success Index)**: Target ≥ 0.55 (Convective cores ≥ 35 dBZ)
- **Target POD (Probability of Detection)**: Target ≥ 0.70
- **Target FAR (False Alarm Ratio)**: Target ≤ 0.35
- **Target HSS (Heidke Skill Score)**: Target ≥ 0.45
- **Target GPU Latency**: Target < 3.0s per 512x512 tile
- **Current Status**: Pilot checkpoint initialized. Formal CSI/POD/FAR benchmarking is computed on held-out storm validation splits (`ml/src/evaluate.py`).
