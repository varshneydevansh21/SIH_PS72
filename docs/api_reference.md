# StormSight API Reference

## Base URL
- Local: `http://localhost:8001`
- Production: `https://sih-ps72.onrender.com`

## Endpoints

### 1. Nowcast
- `GET /nowcast/`: Returns the latest 8-step nowcast cells, centroids, probabilities, and severities.
- `GET /nowcast/{nowcast_id}`: Returns a specific nowcast prediction by ID.
- `POST /nowcast/trigger`: Manually triggers a real-time tensor fusion and inference cycle.

### 2. Alerts
- `GET /alerts/`: Returns active thunderstorm and lightning warnings with 8-point GeoJSON bounding polygons and severity levels.
- `GET /alerts/{alert_id}`: Returns a specific alert by ID.

### 3. Radar
- `GET /radar/latest`: Returns latest radar scan metadata across DWR stations (Delhi, Kolkata, Mumbai, Chennai, Patna, Hyderabad).
- `GET /radar/station/{station_id}`: Returns scans for a specific radar station.

### 4. Lightning
- `GET /lightning/recent?minutes=15`: Returns individual lightning strikes (CG/IC) in the last N minutes.
- `GET /lightning/density`: Returns computed 2D lightning density grid for a bounding box.

### 5. Ingestion
- `POST /ingest/radar`: Ingests and processes DWR radar sweeps.
- `POST /ingest/satellite`: Ingests and processes INSAT-3D/3DR TIR1/WV channels.
- `POST /ingest/lightning`: Ingests ILDN/GLD360 lightning flash points.
- `POST /ingest/nwp`: Ingests GFS/NCUM GRIB2 forecast instability fields.

### 6. WebSocket Live Stream
- `WS /ws/nowcast`: Real-time bidirectional WebSocket stream pushing `NOWCAST_FRAME_READY` and `NEW_ALERT` events.
