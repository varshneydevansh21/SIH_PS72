<div align="center">

# 🌩️ StormSight

### AI/ML-Powered Thunderstorm & Lightning Nowcasting Platform

**Smart India Hackathon 2026 | Problem Statement PS26072**

*Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)*

**🌐 Live Deployments:**
- **Frontend Dashboard:** [https://stormsight-frontend.vercel.app](https://stormsight-frontend.vercel.app)
- **Backend API (Docs):** [https://sih-ps72.onrender.com/docs](https://sih-ps72.onrender.com/docs)

[![Frontend](https://img.shields.io/badge/Frontend-React_19-61DAFB?style=flat-square&logo=react)](https://stormsight-frontend.vercel.app/dashboard)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://sih-ps72.onrender.com/docs)
[![ML](https://img.shields.io/badge/ML-PyTorch_2.14-EE4C2C?style=flat-square&logo=pytorch)](./ml/)
[![Database](https://img.shields.io/badge/Database-PostGIS-336791?style=flat-square&logo=postgresql)](./backend/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./LICENSE)

[Live Dashboard](https://stormsight-frontend.vercel.app/dashboard) · [API Docs](https://sih-ps72.onrender.com/docs) · [Architecture](https://stormsight-frontend.vercel.app/architecture) · [Presentation](./docs/SIH2026_PS26072_Presentation_Master.md)

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [ML Model Architecture](#-ml-model-architecture)
- [Database Schema](#-database-schema)
- [API Reference](#-api-reference)
- [Getting Started](#-getting-started)
- [Frontend Dashboard](#-frontend-dashboard)
- [Data Sources](#-data-sources)
- [Performance Targets](#-performance-targets)
- [Roadmap](#-roadmap)
- [Team](#-team)
- [References](#-references)

---

## 🎯 Problem Statement

> **PS26072**: AIML based Nowcasting of thunderstorm and lightning using atmospheric observation including multiple radars, satellite, lightning and model data.

**India loses 2,500+ lives annually** to thunderstorms and lightning — the country's deadliest natural hazard. Current forecasting systems rely on NWP models that take **6+ hours** to compute at **25 km resolution**, far too coarse and slow for localized, rapidly-evolving convective weather events.

### Key Gaps Addressed
| Gap | Current State | StormSight Solution |
|:---|:---|:---|
| Data Integration | Fragmented across 4+ systems | **Unified tensor fusion pipeline** |
| Prediction Speed | 6+ hour NWP cycles | **< 90 second end-to-end latency** |
| Spatial Resolution | 13–25 km grids | **2 km Cartesian grids** |
| Lead Time | 30–60 min (optical flow only) | **0–120 min (AI-driven)** |
| Automation | Manual meteorologist interpretation | **Fully automated alert generation** |

---

## 💡 Solution Overview

StormSight is a **multi-modal spatio-temporal AI engine** that fuses four distinct atmospheric data sources into a unified deep learning pipeline, producing high-resolution thunderstorm and lightning probability maps with automated severity-classified alerts.

### Three Core Innovations

1. **Multi-Source Tensor Fusion** — First system to fuse Radar + Satellite + Lightning + NWP into a single `[B, T, C, H, W]` tensor for deep learning inference
2. **UNet-ConvLSTM Architecture** — Spatial encoder-decoder (UNet) combined with temporal sequence modeling (ConvLSTM) for physics-aware storm evolution prediction
3. **Sub-90-Second Pipeline** — Kafka-based streaming architecture ensures predictions reach the dashboard within 90 seconds of raw sensor data arrival

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA INGESTION LAYER                        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ IMD DWR  │  │ INSAT-3D │  │  ILDN /  │  │ GFS/NCUM │       │
│  │  Radar   │  │ Satellite│  │  GLD360  │  │   NWP    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │ Py-ART      │ Satpy       │ GeoPandas   │ xarray       │
│       ▼             ▼             ▼             ▼              │
│  ┌─────────────── Apache Kafka ──────────────────┐             │
│  │  radar.scans  │ satellite.frames │ lightning   │             │
│  └──────────────────────┬────────────────────────┘             │
│                         ▼                                       │
│  ┌──────────── MinIO Object Store ────────────────┐             │
│  │  Binary Blobs (NetCDF4, HDF5, GRIB2)           │             │
│  └──────────────────────┬─────────────────────────┘             │
├─────────────────────────┼───────────────────────────────────────┤
│              INTELLIGENCE ENGINE                                │
│                         ▼                                       │
│  ┌─────────── Tensor Fusion Module ───────────────┐             │
│  │  Reproject → Align → Stack → [B,T=4,C=7,H,W]  │             │
│  └──────────────────────┬─────────────────────────┘             │
│                         ▼                                       │
│  ┌─────────── UNet-ConvLSTM Model ────────────────┐             │
│  │  PyTorch 2.14 + CUDA GPU Inference             │             │
│  │  Output: [B, T_out=8, C=2, H=512, W=512]      │             │
│  └──────────────────────┬─────────────────────────┘             │
│                         ▼                                       │
│  ┌─────────── Post-Processing ────────────────────┐             │
│  │  Threshold → Classify → Generate Alert Polygons │             │
│  └──────────────────────┬─────────────────────────┘             │
├─────────────────────────┼───────────────────────────────────────┤
│              SERVING & PRESENTATION                             │
│                         ▼                                       │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐          │
│  │ PostgreSQL │  │   Redis    │  │   FastAPI         │          │
│  │ + PostGIS  │  │  Pub/Sub   │  │   REST + WS      │          │
│  └─────┬──────┘  └─────┬──────┘  └────────┬─────────┘          │
│        └───────────────┼──────────────────┘                     │
│                        ▼                                        │
│  ┌──────────── React Dashboard ───────────────────┐             │
│  │  Leaflet Maps │ Alert Panels │ Forecast Timeline│             │
│  └────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology | Version | Purpose |
|:---|:---|:---|:---|
| **Frontend** | React + TypeScript | 19.x | SPA with interactive dashboard |
| **Build Tool** | Vite | 6.x | Fast HMR development server |
| **Map Engine** | Leaflet (react-leaflet) | 5.x | Geospatial visualization |
| **State** | Zustand | 5.x | Lightweight reactive state management |
| **Styling** | Tailwind CSS | 4.x | Utility-first responsive design |
| **Backend** | FastAPI | 0.141 | Async REST + WebSocket server |
| **Language** | Python | 3.11 | Backend + ML |
| **Database** | PostgreSQL + PostGIS | 17 + 3.5 | Spatial queries & alert storage |
| **ORM** | SQLAlchemy + Alembic | 2.1 | Async ORM + migrations |
| **Cache** | Redis | 8.x | Real-time event Pub/Sub |
| **Streaming** | Apache Kafka | 3.x | Sensor data streaming pipeline |
| **Object Store** | MinIO | — | S3-compatible binary blob storage |
| **ML Framework** | PyTorch | 2.14 | Deep learning training + inference |
| **ML Libraries** | Py-ART, Satpy, xarray | — | Sensor-specific data processing |
| **Containers** | Docker + Compose | — | Reproducible deployments |

---

## 📁 Project Structure

```
SIH_PS72/
├── README.md                              # This file
├── ROADMAP.md                             # Development roadmap
├── Makefile                               # Build shortcuts
│
├── frontend/                              # React + Vite Frontend
│   ├── src/
│   │   ├── App.tsx                        # Router (Home, Architecture, Dashboard)
│   │   ├── main.tsx                       # Entry point
│   │   ├── index.css                      # Global styles
│   │   ├── pages/
│   │   │   ├── Home.tsx                   # Landing page
│   │   │   ├── Architecture.tsx           # System architecture page
│   │   │   └── DashboardApp.tsx           # Dashboard shell (Sidebar + Topbar + Views)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx                # Navigation sidebar (8 views)
│   │   │   ├── Topbar.tsx                 # Search, region filter, live clock, alerts
│   │   │   ├── Dashboard/
│   │   │   │   ├── DashboardView.tsx      # Main dashboard (stats + map + alerts)
│   │   │   │   ├── NowcastMap.tsx         # Leaflet map with alert overlays
│   │   │   │   └── ForecastTimelineView.tsx # Multi-panel forecast evolution
│   │   │   └── ui/                        # Reusable UI primitives
│   │   ├── store/
│   │   │   └── useNowcastStore.ts         # Zustand store (API integration)
│   │   ├── types/
│   │   │   └── nowcast.ts                 # TypeScript types + risk level config
│   │   └── lib/
│   │       ├── api.ts                     # Axios API client
│   │       └── locations.ts               # 700+ Indian location records
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── backend/                               # FastAPI Backend
│   ├── app/
│   │   ├── main.py                        # FastAPI app factory + CORS + routers
│   │   ├── core/
│   │   │   └── config.py                  # Pydantic settings (env vars)
│   │   ├── db/
│   │   │   └── session.py                 # Async SQLAlchemy engine + session factory
│   │   ├── models/                        # SQLAlchemy ORM models
│   │   │   ├── base.py                    # Declarative base
│   │   │   ├── nowcast.py                 # Nowcast (thunderstorm predictions)
│   │   │   ├── alert.py                   # Alert (severity-classified warnings)
│   │   │   ├── lightning_event.py         # LightningEvent (individual strikes)
│   │   │   ├── radar_scan.py              # RadarScan (DWR metadata)
│   │   │   ├── satellite_frame.py         # SatelliteFrame (INSAT metadata)
│   │   │   └── nwp_run.py                 # NWPRun (GFS/NCUM metadata)
│   │   ├── api/                           # API route modules
│   │   │   ├── health.py                  # GET /health
│   │   │   ├── nowcast.py                 # GET /nowcast, POST /nowcast/trigger
│   │   │   ├── alerts.py                  # GET /alerts
│   │   │   ├── radar.py                   # GET /radar/latest
│   │   │   ├── lightning.py               # GET /lightning/recent
│   │   │   ├── ingest.py                  # POST /ingest/radar, /ingest/lightning
│   │   │   └── ws.py                      # WebSocket /ws/live-stream
│   │   └── services/
│   │       └── nowcast_adapter.py         # ML inference adapter (stub)
│   ├── alembic/                           # Database migrations
│   │   ├── env.py                         # Migration environment config
│   │   └── versions/                      # Generated migration scripts
│   ├── scripts/
│   │   └── seed_demo_data.py              # Database seeding for demo
│   ├── docker-compose.yml                 # DB + Redis + API containers
│   ├── Dockerfile                         # API container image
│   ├── requirements.txt                   # Python dependencies
│   └── .env                               # Environment variables
│
├── ml/                                    # Machine Learning Pipeline
│   ├── src/
│   │   ├── model.py                       # UNet-ConvLSTM architecture (PyTorch)
│   │   ├── dataset.py                     # Custom dataset loader
│   │   ├── train.py                       # Training loop
│   │   ├── evaluate.py                    # Evaluation metrics (CSI, POD, FAR)
│   │   └── fusion.py                      # Multi-source tensor fusion module
│   ├── configs/                           # Training hyperparameters
│   ├── checkpoints/                       # Saved model weights
│   └── inference.py                       # Production inference entry point
│
├── ingest/                                # Data ingestion daemons
│   └── (Kafka consumer scripts for radar, satellite, lightning, NWP)
│
├── data/                                  # Raw + processed data storage
├── model_artifacts/                       # Exported model artifacts
├── scripts/                               # Utility scripts
│
└── docs/                                  # Documentation
    ├── SIH2026_PS26072_Presentation_Master.md  # Full SIH presentation
    ├── SIH_Documentation.md                     # Project documentation
    ├── StormSight_Complete_Research_Report.md    # Research report
    ├── architecture.md                          # Architecture deep-dive
    ├── api_reference.md                         # API documentation
    └── data_sources.md                          # Data source specifications
```

---

## 🧠 ML Model Architecture

### UNet-ConvLSTM Hybrid Network

The model combines **spatial feature extraction** (UNet encoder-decoder) with **temporal sequence learning** (Convolutional LSTM) to predict storm evolution.

```
Input: [B, T_in=4, C=7, H=512, W=512]
                    │
        ┌───────────┴───────────┐
        │    UNet Encoder       │  (Per-timestep spatial encoding)
        │  Conv2d → BN → ReLU  │
        │  MaxPool (4 levels)   │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │    ConvLSTM Bridge    │  (Temporal modeling across T steps)
        │  Learns storm motion  │
        │  & growth/decay       │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │    UNet Decoder       │  (Spatial upsampling with skip connections)
        │  ConvTranspose2d      │
        │  + Skip Connections   │
        └───────────┬───────────┘
                    │
Output: [B, T_out=8, C_out=2, H=512, W=512]
    C₀: Predicted Reflectivity (0–120 min)
    C₁: Lightning Strike Probability (0–120 min)
```

### Input Channels (C=7)

| # | Source | Channel | Preprocessing |
|---|---|---|---|
| C₀ | Radar | Reflectivity (Z_H) | Normalized [0,1] where 1.0 = 70 dBZ |
| C₁ | Satellite | TIR1 Brightness Temp | Kelvin → [0,1] normalization |
| C₂ | Satellite | Water Vapor (WV) | Kelvin → [0,1] normalization |
| C₃ | Derived | BTD (TIR1 − WV) | Indicates deep convection |
| C₄ | Lightning | Strike Density | Gaussian KDE from sparse points |
| C₅ | NWP | CAPE | Convective Available Potential Energy |
| C₆ | NWP | CIN | Convective Inhibition |

### Custom Loss Function
```
L_total = α · L_WB-MSE + β · (1 − SSIM) + γ · L_Soft-CSI

Where:
  L_WB-MSE  = Weighted Balanced MSE (exponentially penalizes missed severe storms)
  SSIM      = Structural Similarity Index (preserves spatial structure)
  L_Soft-CSI = Differentiable Critical Success Index (optimizes verification metric)
  α=1.0, β=0.3, γ=0.5
```

---

## 🗄 Database Schema

All tables use **UUID primary keys** and **PostGIS geometry columns** with SRID 4326 (WGS84).

### Entity Relationship

```
nowcasts ──┐
           │ 1:N
           ├──── alerts
           │
lightning_events (independent)
radar_scans (independent)
satellite_frames (independent)
nwp_runs (independent)
```

### Table Definitions

<details>
<summary><b>nowcasts</b> — Thunderstorm predictions</summary>

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique identifier |
| run_time | TIMESTAMPTZ | When the prediction was generated |
| lead_time_minutes | INTEGER | Forecast lead time (15, 30, 45, ..., 120) |
| affected_area | GEOMETRY(POLYGON, 4326) | Storm coverage polygon |
| storm_intensity_class | VARCHAR | `moderate`, `severe`, `extreme` |
| probability | FLOAT | Thunderstorm probability (0.0–1.0) |
| details | JSON | Speed, direction, hail probability |
| created_at | TIMESTAMPTZ | Record creation timestamp |

</details>

<details>
<summary><b>alerts</b> — Severity-classified warnings</summary>

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique identifier |
| nowcast_id | UUID (FK → nowcasts) | Associated prediction |
| alert_type | VARCHAR | `Thunderstorm Warning`, `Heavy Rainfall`, `Squall Line` |
| severity | VARCHAR | `moderate`, `severe`, `extreme` |
| issue_time | TIMESTAMPTZ | When alert was issued |
| valid_until | TIMESTAMPTZ | Alert expiry time |
| alert_area | GEOMETRY(POLYGON, 4326) | Alert coverage polygon |
| message | VARCHAR | Human-readable warning message |

</details>

<details>
<summary><b>lightning_events</b> — Individual lightning strikes</summary>

| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Unique identifier |
| event_time | TIMESTAMPTZ | Strike timestamp |
| location | GEOMETRY(POINT, 4326) | Strike coordinates |
| current_ka | FLOAT | Peak current in kiloamperes |
| polarity | INTEGER | +1 or −1 |

</details>

---

## 📡 API Reference

Base URL: `http://localhost:8001`

### Health
```http
GET /health
```
Returns system health status and database connectivity.

### Nowcast
```http
GET /nowcast                    # Latest 10 thunderstorm predictions
GET /nowcast/{id}               # Specific prediction details
POST /nowcast/trigger           # Manually trigger inference cycle
```

### Alerts
```http
GET /alerts                     # All active alerts (valid_until > now)
GET /alerts/{id}                # Specific alert with nowcast relation
```

### Radar
```http
GET /radar/latest               # Latest radar scan per DWR station
GET /radar/station/{station_id} # Recent scans for specific station
```

### Lightning
```http
GET /lightning/recent?minutes=30  # Recent strokes (last N minutes)
GET /lightning/density            # Density grid for bounding box
```

### Data Ingestion
```http
POST /ingest/radar              # Ingest new radar scan metadata
POST /ingest/lightning          # Ingest lightning event batch
```

### WebSocket
```
WS /ws/live-stream              # Real-time event stream
```

---

## 🚀 Getting Started

### Prerequisites
- **Docker Desktop** (with Docker Compose)
- **Node.js** ≥ 18.x (for frontend development)
- **Git**

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/varshneydevansh21/SIH_PS72.git
cd SIH_PS72

# 2. Start backend infrastructure (PostgreSQL + PostGIS, Redis, API)
cd backend
docker compose up -d db redis
docker compose build api
docker compose run --rm api alembic -c alembic.ini upgrade head    # Apply migrations
docker compose run --rm api python scripts/seed_demo_data.py       # Seed demo data
docker compose up -d api                                           # Start API server

# 3. Start frontend development server
cd ../frontend
npm install
npm run dev

# 4. Open in browser
# Dashboard:    http://localhost:5173/dashboard
# API Docs:     http://localhost:8001/docs
# Landing Page: http://localhost:5173/
```

### Environment Variables

Create `backend/.env` with:
```ini
# Database (PostgreSQL + PostGIS)
DATABASE_URL=postgresql+asyncpg://stormsight:stormsight_secure@db:5432/stormsight
DATABASE_SYNC_URL=postgresql+psycopg2://stormsight:stormsight_secure@db:5432/stormsight

# Application
DEBUG=True
CORS_ORIGINS=*

# Redis
REDIS_URL=redis://redis:6379/0

# ML (will be configured when model is trained)
ML_FORCE_STUB=True
```

---

## 🖥 Frontend Dashboard

### Pages & Routes

| Route | Page | Description |
|---|---|---|
| `/` | Home | Landing page with project overview |
| `/architecture` | Architecture | System architecture visualization |
| `/dashboard` | Dashboard App | Full operational nowcasting dashboard |

### Dashboard Views (Sidebar Navigation)

| View | Status | Description |
|---|---|---|
| **Dashboard** | ✅ Complete | Stats cards + Map + Active warnings panel |
| **Nowcast Map** | ✅ Complete | Full-screen interactive Leaflet map |
| **Forecast Timeline** | ✅ Complete | 6-panel predicted evolution (Now → +120 min) |
| **Observations** | 🔜 Planned | Raw sensor data display |
| **Alerts** | 🔜 Planned | Dedicated alert management |
| **Analytics** | 🔜 Planned | Historical performance metrics |
| **Historical Replay** | 🔜 Planned | Past event analysis |
| **Settings** | 🔜 Planned | Configuration panel |

### Key Features
- 🗺️ **Interactive Leaflet Map** with 6-tier risk zone overlays
- 🔍 **Location Search** with autocomplete (700+ Indian cities)
- 📊 **Live Statistics** from backend API (auto-refresh every 5 min)
- ⚠️ **Active Warnings** panel sorted by severity
- 🕐 **Live Clock** showing current date/time
- 🔴 **Alert Badge** with pulse animation for high-risk conditions
- 🌐 **Region Filter** (All India, North, South, East, West, Central, NE)

---

## 📊 Data Sources

| Source | Provider | Format | Cadence | Resolution | Library |
|---|---|---|---|---|---|
| **Doppler Radar** | IMD DWR Network | NetCDF4/HDF5 | 10 min | ~1–2 km | Py-ART |
| **Satellite** | MOSDAC INSAT-3D/3DR | HDF5 | 15–30 min | 4 km (IR) | Satpy |
| **Lightning** | ILDN / GLD360 | JSON/CSV | Continuous | Point coords | GeoPandas |
| **NWP Models** | GFS / NCUM | GRIB2 | 6-hourly | 13–25 km | xarray, cfgrib |

---

## 🎯 Performance Targets

| Metric | Target | Description |
|---|---|---|
| CSI (Critical Success Index) | ≥ 0.55 | For ≥ 35 dBZ threshold |
| POD (Probability of Detection) | ≥ 0.70 | Minimize missed severe storms |
| FAR (False Alarm Ratio) | ≤ 0.35 | Minimize false alarms |
| Lead Time | 0–120 min | 8 intervals at 15 min each |
| Spatial Resolution | 2 km | 512×512 grid |
| End-to-End Latency | < 90 sec | Sensor data → Dashboard |
| Inference Latency | < 3 sec | GPU inference per batch |

---

## 🗺 Roadmap

- [x] Project scaffolding & architecture design
- [x] Frontend dashboard (React + Leaflet + Tailwind)
- [x] Backend API (FastAPI + SQLAlchemy + PostGIS)
- [x] Database schema & migrations (Alembic)
- [x] Demo data seeding (thunderstorm cells, alerts, lightning)
- [x] Frontend ↔ Backend integration (Zustand + fetch)
- [ ] UNet-ConvLSTM model implementation
- [ ] Tensor fusion module (multi-source data alignment)
- [ ] Model training on IMD historical data
- [ ] Kafka streaming data pipeline
- [ ] Real-time WebSocket push notifications
- [ ] Production deployment (Kubernetes)

---

## 👥 Team

**Team StormSight** — Smart India Hackathon 2026

---

## 📚 References

1. Shi, X., et al. (2015). *Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting.* NeurIPS 2015.
2. Agrawal, S., et al. (2019). *Machine Learning for Precipitation Nowcasting from Radar Images.* Google Research.
3. Ronneberger, O., et al. (2015). *U-Net: Convolutional Networks for Biomedical Image Segmentation.* MICCAI 2015.
4. Ravuri, S., et al. (2021). *Skillful precipitation nowcasting using deep generative models of radar.* Nature, 597.
5. Leinonen, J., et al. (2023). *Seamless Large-Area Precipitation Nowcasting.* IEEE TGRS.

### Data Source Links
- IMD Radar: https://mausam.imd.gov.in/
- MOSDAC Satellite: https://mosdac.gov.in/
- GFS Models: https://nomads.ncep.noaa.gov/

---

<div align="center">

*Built with ❤️ for Smart India Hackathon 2026*

**© 2026 Team StormSight**

</div>
