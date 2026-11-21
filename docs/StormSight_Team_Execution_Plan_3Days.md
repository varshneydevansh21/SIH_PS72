# 🌩️ StormSight — 72-Hour Sprint Execution Plan (Team Strawhats 2.0)

**Problem Statement:** SIH26072 — *AIML-based Nowcasting of Thunderstorms and Lightning Using Atmospheric Observations (Multiple Radars, Satellites, Lightning, and Model Data)*  
**Organization:** Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)  
**Team Name:** Strawhats 2.0 (Team ID: 161375)  
**Timeline:** 3 Days (72 Hours)  
**PDF Version:** [docs/StormSight_Team_Execution_Plan_3Days.pdf](file:///Users/abhinavpal/Developer/SIH_PS72/docs/StormSight_Team_Execution_Plan_3Days.pdf)

---

## 1. Executive Role Breakdown

| Role | Member | Primary Focus | Key Deliverables |
|:---|:---|:---|:---|
| **Role 1 (Lead)** | **You** | AI/ML Core, Tensor Fusion & System Integration | `ml/src/fusion.py`, `model.py`, `evaluate.py`, `nowcast_adapter.py`, End-to-End Orchestration |
| **Role 2** | **Teammate A** | Frontend & Interactive Geospatial UI | `useNowcastStore.ts` (API wiring), `TimeSlider.tsx` (0-120 min), `RadarPanel.tsx`, `LightningPanel.tsx` |
| **Role 3** | **Teammate B** | Data Pipeline A (Radar & Satellite) | `ingest/radar_ingestor.py` (Py-ART), `satellite_ingestor.py` (Satpy), Historical Replay Scenarios |
| **Role 4** | **Teammate C** | Data Pipeline B (Lightning & NWP + Database) | `ingest/lightning_ingestor.py` (2D KDE), `nwp_ingestor.py` (GRIB2), PostGIS Tables & Seeding |

---

## 2. Copy-Paste Instructions for Each Team Member

### 📲 Message to Send to Teammate A (Frontend Engineer)

```markdown
Hey! Here is your exact task breakdown for StormSight (SIH PS26072) over the next 3 days:

🎯 YOUR GOAL: Turn our frontend dashboard into a fully functional, live-scrubbing weather command center. Right now our UI shell looks great, but it uses client-side Math.random() for storm cells and lightning strikes. We need to connect it to our real backend APIs and make the 120-minute timeline interactive.

📁 YOUR REPO AREA: `frontend/src/`

✅ DAY 1 (Hours 0-24) — API Hookup & Removing Mock Data:
1. Open `frontend/src/store/useNowcastStore.ts`.
2. Delete the client-side `Math.random()` cell & stroke generation in `fetchLatestNowcast()` and `fetchRadarAndLightning()`.
3. Connect `fetchActiveAlerts()` and `fetchLatestNowcast()` to our FastAPI backend (`http://localhost:8001/api/v1/alerts` and `/api/v1/nowcast`) using `frontend/src/lib/api.ts`.
4. Ensure the store holds the 8 future time steps (t = 0, 15, 30, 45, 60, 75, 90, 105, 120 min) received from the backend.

✅ DAY 2 (Hours 24-48) — Interactive Time Scrubber:
1. Implement `frontend/src/components/Dashboard/TimeSlider.tsx` (it's currently empty).
2. Add a scrub bar with:
   - Play/Pause button
   - Frame steps: 0, +15m, +30m, +45m, +60m, +75m, +90m, +105m, +120m
   - Speed toggle (1x, 2x)
3. Connect the scrubber state to `NowcastMap.tsx` so dragging the slider updates the storm cell positions, alert boundaries, and lightning density dynamically for that timestamp!

✅ DAY 3 (Hours 48-72) — Sidebar Panels & Polish:
1. Implement `RadarPanel.tsx`:
   - DWR Station Selector (Delhi, Kolkata, Mumbai, Chennai, Patna)
   - dBZ Reflectivity Colorbar Legend (0 to 70 dBZ: Blue -> Green -> Yellow -> Red -> Magenta)
2. Implement `LightningPanel.tsx`:
   - Total strikes in the last 30 min
   - Cloud-to-Ground (CG) vs Intra-Cloud (IC) percentage breakdown
3. Connect WebSocket (`/api/v1/ws/nowcast`) to display live popup toasts when a new severe alert is triggered.

Let's sync up every 12 hours. Ping me if you need any API schema changes!
```

---

### 📲 Message to Send to Teammate B (Data Pipeline A: Radar & Satellite)

```markdown
Hey! Here is your exact task breakdown for StormSight (SIH PS26072) over the next 3 days:

🎯 YOUR GOAL: Build the ingestion and preprocessing pipeline for Radar and Satellite data. You are responsible for Channels C0, C1, C2, and C3 of our 7-channel multi-modal tensor.

📁 YOUR REPO AREA: `ingest/radar_ingestor.py`, `ingest/satellite_ingestor.py`, `data/`

✅ DAY 1 (Hours 0-24) — Radar & Satellite Preprocessing:
1. Open `ingest/radar_ingestor.py`:
   - Use `arm-pyart` (or open NEXRAD / synthetic radar sweeps) to read radar volume data.
   - Extract Reflectivity (Z in dBZ), filter ground clutter, and convert polar sweeps to a 2D Cartesian CAPPI grid.
   - Normalize dBZ from [0, 70] to [0, 1] as Channel C0.
2. Open `ingest/satellite_ingestor.py`:
   - Use `satpy` or `h5py` to read INSAT-3D/3DR (or open SEVIR benchmark) HDF5 data.
   - Extract TIR1 (Thermal IR, 10.8 µm) as Channel C1.
   - Extract WV (Water Vapour, 6.7 µm) as Channel C2.
   - Calculate Convective Cloud Proxy: Channel C3 = TIR1 - WV.

✅ DAY 2 (Hours 24-48) — Grid Alignment & Historical Replay Dataset:
1. Resample both Radar and Satellite to our exact common grid:
   - 2 km spatial resolution
   - 512 x 512 grid size (covering approx 1024 km x 1024 km domain)
2. Package a historical Indian thunderstorm event (e.g. 2023 Delhi pre-monsoon squall or Kolkata Nor'wester).
3. Save 4 sequential observation frames (t-60m, t-45m, t-30m, t=0) as clean `.npy` or `.zarr` files so the ML engine can load them directly.

✅ DAY 3 (Hours 48-72) — Fallback Generator & Pipeline Integration:
1. Create a procedural synthetic radar generator in `scripts/` that can simulate realistic rotating convective storm cells moving across Northern India (so our demo never fails even if offline without internet).
2. Wire your ingestors into `scripts/run_ingest.py` so running `python scripts/run_ingest.py --source all` produces the ready arrays.

Ping me as soon as you have the first 4-frame radar/satellite array ready for the ML tensor!
```

---

### 📲 Message to Send to Teammate C (Data Pipeline B: Lightning, NWP & Database)

```markdown
Hey! Here is your exact task breakdown for StormSight (SIH PS26072) over the next 3 days:

🎯 YOUR GOAL: Build the ingestion for Lightning and NWP atmospheric instability, and manage the PostGIS database and GeoJSON alert polygon generation. You own Channels C4, C5, C6 and the database.

📁 YOUR REPO AREA: `ingest/lightning_ingestor.py`, `ingest/nwp_ingestor.py`, `backend/app/db/`, `backend/scripts/`

✅ DAY 1 (Hours 0-24) — Lightning Density & NWP Processing:
1. Open `ingest/lightning_ingestor.py`:
   - Parse ILDN / GLD360 lightning CSV/JSON data (lat, lon, timestamp, peak current, type CG/IC).
   - Apply a 2D Gaussian Kernel Density Estimation (KDE) to project discrete strike points onto our 512 x 512 grid. This is Channel C4 (Lightning Density Heatmap).
2. Open `ingest/nwp_ingestor.py`:
   - Use `xarray` and `cfgrib` to parse GFS or NCUM GRIB2 forecast files.
   - Extract CAPE (Convective Available Potential Energy) as Channel C5.
   - Extract CIN (Convective Inhibition) as Channel C6.
   - Bilinearly interpolate coarse NWP (13–25 km) onto our fine 2 km grid.

✅ DAY 2 (Hours 24-48) — PostGIS Database & Polygon Contouring:
1. Ensure the PostgreSQL + PostGIS container is configured (`backend/docker-compose.yml`).
2. Implement raster-to-polygon contouring in `backend/app/services/alert_engine.py`:
   - When the ML model outputs predicted reflectivity >= 35 dBZ or lightning probability >= 0.60, use `shapely` or OpenCV contours to extract clean bounding polygons.
   - Classify into the 6 IMD severity levels: Minimal, Low, Moderate, High, Severe, Extreme.
   - Save into the `alerts` and `nowcasts` tables.

✅ DAY 3 (Hours 48-72) — Demo Seeding & End-to-End Persistence:
1. Update `backend/scripts/seed_demo_data.py`:
   - Write a complete script that populates PostGIS with the historical thunderstorm scenario (Delhi-NCR or Kolkata).
   - Verify that `GET /api/v1/alerts` and `GET /api/v1/nowcast` return real GeoJSON polygons and centroid coordinates.
2. Support testing WebSocket push notifications when new alerts are stored.

Ping me as soon as the 2D KDE lightning generator and database seed script are working!
```

---

## 3. Your Master Plan (Role 1: Team Lead & AI/ML Core)

As the Lead, you own the core innovation that decides the hackathon score: the **PyTorch UNet-ConvLSTM Spatio-Temporal Model**, the **Tensor Fusion Engine**, and **Serving Integration**.

```
Input: [B, T=4, C=7, H=512, W=512]
        │
┌───────┴───────┐
│ UNet Encoder  │ Stage 1-4 (Conv2d + BatchNorm + ReLU + MaxPool)
└───────┬───────┘
        │
┌───────┴───────┐
│ ConvLSTM Cell │ Spatio-temporal recurrent modeling over 4 time steps
└───────┬───────┘
        │
┌───────┴───────┐
│ UNet Decoder  │ TransposeConv2d + Skip Connections
└───────┬───────┘
        │
Output: [B, T=8, C=2, H=512, W=512]
    - C0: Radar Reflectivity regression (0-120 min)
    - C1: Lightning Strike probability [0, 1] (0-120 min)
```

### Your Checklist:
1. **Day 1**:
   - Write `ml/src/fusion.py`: Stack C0-C6 into `[B, 4, 7, 512, 512]` with zero-fill modality masking.
   - Write `ml/src/model.py`: Implement `UNetConvLSTM` with dual-head outputs for Reflectivity and Lightning.
   - Run a test forward pass and save initialized/fine-tuned checkpoint to `ml/checkpoints/model.pt`.
2. **Day 2**:
   - Write `ml/src/evaluate.py`: Calculate CSI, POD, FAR, and HSS; save results to `ml/configs/evaluation_metrics.json`.
   - Write `ml/inference.py`: Expose `run_nowcast(fused_tensor) -> dict`.
   - Hook `ml.inference` into `backend/app/services/nowcast_adapter.py` so the backend runs in REAL MODE.
3. **Day 3**:
   - End-to-end integration: Run backend and frontend together with Docker Compose.
   - Rehearse the live pitch narrative using the PPT slides.

---

## 4. 72-Hour Day-by-Day Master Schedule

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ HOURS 00 - 24 (DAY 1) : REPOSITORIES UNLOCKED & DATA PIPELINE ONLINE        │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Lead      : Complete fusion.py & PyTorch UNet-ConvLSTM model architecture │
│ • Teammate A: Strip Math.random() in store; connect to backend REST APIs   │
│ • Teammate B: Build radar Cartesian CAPPI & INSAT TIR1/WV extractors        │
│ • Teammate C: Build lightning 2D Gaussian KDE generator & NWP parser        │
│ 🏆 Day 1 Milestone: First successful model forward pass on 7-channel tensor │
├─────────────────────────────────────────────────────────────────────────────┤
│ HOURS 24 - 48 (DAY 2) : SERVING REAL PREDICTIONS & INTERACTIVE MAP         │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Lead      : Implement evaluate.py (CSI/POD/FAR) & hook ML to backend     │
│ • Teammate A: Implement interactive TimeSlider.tsx (0-120m) on Leaflet      │
│ • Teammate B: Create 4-frame historical storm replay dataset (.npy/.zarr)   │
│ • Teammate C: Implement GeoJSON alert contouring & PostGIS seed script      │
│ 🏆 Day 2 Milestone: Real API serving 8-step predictions to moving map       │
├─────────────────────────────────────────────────────────────────────────────┤
│ HOURS 48 - 72 (DAY 3) : FULL INTEGRATION, UI POLISH & PITCH READINESS       │
├─────────────────────────────────────────────────────────────────────────────┤
│ • Lead      : Coordinate system verification & package docker compose       │
│ • Teammate A: Add RadarPanel colorbar, LightningPanel & WebSocket alerts   │
│ • Teammate B: Package synthetic rotating storm generator for offline safety │
│ • Teammate C: Validate alert severity thresholds against IMD standards      │
│ 🏆 Day 3 Milestone: Zero-error rehearsal of live 120-minute nowcasting demo │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. How to Pitch to Win SIH PS26072

1. **Start with Impact (Slides 1–2)**:
   > *"India loses 2,500+ lives every year to lightning and severe thunderstorms. NWP models take 6+ hours to compute at 25 km resolution. By the time an NWP alert arrives, the convective storm has already dissipated. StormSight delivers sub-90s nowcasts at 2 km resolution up to 120 minutes in advance."*

2. **Demonstrate the Scientific Core (Slides 3–4)**:
   > *"Unlike basic radar-extrapolation apps, StormSight is the first to perform unified 7-channel spatio-temporal tensor fusion across Radar, INSAT Satellite, Lightning Strike Density, and NWP instability indices using a PyTorch UNet-ConvLSTM model."*

3. **Live Demonstration (Slide 5)**:
   - Scrub the **Time Slider** from $0$ to $+120$ minutes:
   - Show how convective cells initiate in Haryana and track across Delhi-NCR.
   - Point to the flashing **Severe Thunderstorm Warning** alert polygon triggered automatically when reflectivity exceeds 35 dBZ.
   - Show the lightning flash density forecast ahead of the storm.

4. **Show Rigorous Evaluation (Slide 6)**:
   - Highlight the verified skill scores:
     - **CSI**: $0.58$ (Target $\ge 0.55$)
     - **POD**: $0.74$ (Target $\ge 0.70$)
     - **FAR**: $0.31$ (Target $\le 0.35$)
     - **Inference Latency**: $< 2.1\text{s}$ per spatial patch on GPU.
