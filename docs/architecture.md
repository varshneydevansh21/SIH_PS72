# StormSight Architecture & System Design

## 1. High-Level Flow
```
Observations (Radar, INSAT, Lightning, NWP)
   ↓
Data Ingestion Layer (Py-ART, Satpy, GeoPandas, xarray)
   ↓
Tensor Fusion Module [B, T=4, C=7, H=512, W=512]
   ↓
UNet-ConvLSTM Spatio-Temporal Model
   ↓
Dual-Head Forecast [B, T=8, C=2, H=512, W=512]
   ↓
Post-Processing & Polygon Contouring Engine
   ↓
Serving Layer (FastAPI REST + WebSocket + PostGIS)
   ↓
Presentation Layer (React 19 + Leaflet Interactive Dashboard)
```

## 2. Ingestion & Preprocessing
- **Radar**: Polar sweeps converted to Cartesian CAPPI grid, clutter filtered, normalized [0, 70] dBZ.
- **Satellite**: INSAT TIR1 (10.8 µm) and WV (6.7 µm) channels extracted, convective difference proxy computed.
- **Lightning**: Sparse flash points smoothed via 2D Gaussian Kernel Density Estimation (KDE).
- **NWP**: GFS/NCUM CAPE and CIN fields interpolated onto the target 2km grid.

## 3. Serving & Storage
- **Database**: PostgreSQL 15 + PostGIS 3.3 storing nowcasts, alerts, and lightning stroke events.
- **In-Memory Cache**: Redis for real-time pub/sub distribution.
- **Streaming**: FastAPI WebSocket broadcast manager pushing updates to connected browser clients.
