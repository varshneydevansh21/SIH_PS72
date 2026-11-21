#!/usr/bin/env python3
"""
StormSight - SIH 2026 Team Execution Plan PDF Generator
Generates a multi-page executive plan for Team Strawhats 2.0 (PS26072).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

# Set custom cache directory to avoid permission issues
os.environ["MPLCONFIGDIR"] = ".matplotlib_cache"

OUTPUT_PDF = "docs/StormSight_Team_Execution_Plan_3Days.pdf"
os.makedirs("docs", exist_ok=True)

def draw_card(ax, x, y, w, h, bg_color="#1E293B", border_color="#334155", radius=0.015, alpha=1.0):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=bg_color,
        edgecolor=border_color,
        linewidth=1.2,
        alpha=alpha,
        transform=ax.transAxes,
        zorder=1
    )
    ax.add_patch(box)

def create_page(title=""):
    fig = plt.figure(figsize=(8.27, 11.69), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # Background
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor="#090D16", transform=ax.transAxes, zorder=0))
    
    # Header Accent Bar
    ax.add_patch(plt.Rectangle((0, 0.985), 1, 0.015, facecolor="#F59E0B", transform=ax.transAxes, zorder=2))
    
    # Footer
    ax.text(0.06, 0.025, "StormSight | Smart India Hackathon 2026 | PS26072 | Team Strawhats 2.0",
            fontsize=8, color="#64748B", fontfamily="sans-serif", transform=ax.transAxes)
    ax.text(0.94, 0.025, "Confidential - Team Battle Plan",
            fontsize=8, color="#64748B", fontfamily="sans-serif", ha="right", transform=ax.transAxes)
    
    return fig, ax

def generate_pdf():
    with PdfPages(OUTPUT_PDF) as pdf:
        # =====================================================================
        # PAGE 1: TITLE & 4-PERSON DIVISION OVERVIEW
        # =====================================================================
        fig, ax = create_page()
        
        # Super Header
        ax.text(0.06, 0.94, "SMART INDIA HACKATHON 2026 — TEAM EXECUTION PLAN",
                fontsize=10, fontweight="bold", color="#F59E0B", transform=ax.transAxes)
        ax.text(0.06, 0.89, "StormSight: 72-Hour Sprint Roadmap",
                fontsize=22, fontweight="bold", color="#FFFFFF", transform=ax.transAxes)
        ax.text(0.06, 0.855, "Problem Statement: SIH26072 | MoES & IMD | Theme: Disaster Management",
                fontsize=11, color="#94A3B8", transform=ax.transAxes)
        
        # Summary Box
        draw_card(ax, 0.06, 0.725, 0.88, 0.11, bg_color="#131B2E", border_color="#1E3A8A")
        ax.text(0.08, 0.805, "CORE OBJECTIVE & REALITY CHECK",
                fontsize=10, fontweight="bold", color="#38BDF8", transform=ax.transAxes)
        summary_text = (
            "We have 72 hours to transition StormSight from an initial architectural scaffold into an operational,\n"
            "presentation-ready multi-modal nowcasting platform. The goal is NOT a toy UI with random mock points;\n"
            "it is a functioning system that ingests 4 atmospheric feeds, runs PyTorch UNet-ConvLSTM inference\n"
            "over a 2km grid, calculates real CSI/POD/FAR skill scores, and serves 0-120 min animated storm nowcasts."
        )
        ax.text(0.08, 0.74, summary_text, fontsize=8.5, color="#CBD5E1", linespacing=1.4, transform=ax.transAxes)
        
        # Team Division Table Title
        ax.text(0.06, 0.69, "4-PERSON TEAM ROLE ALLOCATION", fontsize=12, fontweight="bold", color="#FFFFFF", transform=ax.transAxes)
        
        # Role 1: Lead (You)
        draw_card(ax, 0.06, 0.525, 0.88, 0.145, bg_color="#1E293B", border_color="#F59E0B")
        ax.text(0.08, 0.635, "PERSON 1 (YOU - TEAM LEAD): ML CORE, TENSOR FUSION & ARCHITECTURE",
                fontsize=10.5, fontweight="bold", color="#F59E0B", transform=ax.transAxes)
        p1_desc = (
            "• Primary Focus: The core scientific brain of StormSight.\n"
            "• Deliverables: [B, T=4, C=7, H=512, W=512] Tensor Fusion engine, PyTorch UNet-ConvLSTM dual-head network,\n"
            "  loss functions (Weighted MSE + Soft CSI), model evaluation harness (CSI >= 0.55, POD >= 0.70, FAR <= 0.35),\n"
            "  nowcast_adapter.py backend bridge, and overall system integration."
        )
        ax.text(0.08, 0.54, p1_desc, fontsize=8.5, color="#E2E8F0", linespacing=1.35, transform=ax.transAxes)
        
        # Role 2: Frontend
        draw_card(ax, 0.06, 0.365, 0.88, 0.145, bg_color="#1E293B", border_color="#06B6D4")
        ax.text(0.08, 0.475, "PERSON 2: FRONTEND & GEOSPATIAL VISUALIZATION ENGINEER",
                fontsize=10.5, fontweight="bold", color="#38BDF8", transform=ax.transAxes)
        p2_desc = (
            "• Primary Focus: Transforming raw predictions into an intuitive, meteorologist-grade command center.\n"
            "• Deliverables: Replace client-side Math.random() with real backend REST/WebSocket feeds, implement interactive\n"
            "  Time Scrubber (0 to +120 min) on Leaflet, build RadarPanel (dBZ colorbar & station selector), LightningPanel\n"
            "  (CG/IC breakdown), and smooth polygon alert rendering."
        )
        ax.text(0.08, 0.38, p2_desc, fontsize=8.5, color="#E2E8F0", linespacing=1.35, transform=ax.transAxes)
        
        # Role 3: Pipeline A
        draw_card(ax, 0.06, 0.205, 0.88, 0.145, bg_color="#1E293B", border_color="#10B981")
        ax.text(0.08, 0.315, "PERSON 3: DATA PIPELINE ENGINEER A (RADAR & SATELLITE)",
                fontsize=10.5, fontweight="bold", color="#34D399", transform=ax.transAxes)
        p3_desc = (
            "• Primary Focus: Channels C0 (Reflectivity Z), C1 (TIR1), C2 (Water Vapour), C3 (TIR1 - WV).\n"
            "• Deliverables: Implement ingest/radar_ingestor.py and ingest/satellite_ingestor.py using Py-ART & Satpy.\n"
            "  Process HDF5/NetCDF files, resample sweeps to 2km Cartesian grid, build historical storm replay events\n"
            "  (e.g., Delhi convective squall), and provide clean .npy/.zarr arrays to ML engine."
        )
        ax.text(0.08, 0.22, p3_desc, fontsize=8.5, color="#E2E8F0", linespacing=1.35, transform=ax.transAxes)
        
        # Role 4: Pipeline B
        draw_card(ax, 0.06, 0.05, 0.88, 0.145, bg_color="#1E293B", border_color="#A855F7")
        ax.text(0.08, 0.16, "PERSON 4: DATA PIPELINE ENGINEER B (LIGHTNING & NWP + DATABASE)",
                fontsize=10.5, fontweight="bold", color="#C084FC", transform=ax.transAxes)
        p4_desc = (
            "• Primary Focus: Channels C4 (Lightning KDE Heatmap), C5 (NWP CAPE), C6 (NWP CIN) & Database.\n"
            "• Deliverables: Implement ingest/lightning_ingestor.py (2D Gaussian KDE smoothing over strike points) and\n"
            "  ingest/nwp_ingestor.py (GFS/NCUM GRIB2 parsing with xarray/cfgrib). Populate PostGIS tables (lightning_events,\n"
            "  radar_scans, alerts) and write the demo replay seeding scripts."
        )
        ax.text(0.08, 0.065, p4_desc, fontsize=8.5, color="#E2E8F0", linespacing=1.35, transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close(fig)
        
        # =====================================================================
        # PAGE 2: DEEP DIVE - PERSON 1 (LEAD) & PERSON 2 (FRONTEND)
        # =====================================================================
        fig, ax = create_page()
        
        ax.text(0.06, 0.94, "DETAILED ACTION PLAN & INSTRUCTIONS",
                fontsize=10, fontweight="bold", color="#F59E0B", transform=ax.transAxes)
        ax.text(0.06, 0.89, "Person 1 (Lead) & Person 2 (Frontend)",
                fontsize=20, fontweight="bold", color="#FFFFFF", transform=ax.transAxes)
        
        # Card 1: Person 1
        draw_card(ax, 0.06, 0.51, 0.88, 0.355, bg_color="#131B2E", border_color="#F59E0B")
        ax.text(0.08, 0.835, "PERSON 1 (YOU): THE CORE ML & INTEGRATION ENGINE",
                fontsize=11, fontweight="bold", color="#F59E0B", transform=ax.transAxes)
        
        p1_actions = (
            "1. Tensor Fusion Module (ml/src/fusion.py):\n"
            "   • Construct the unified [B, T_in=4, C=7, H=512, W=512] tensor.\n"
            "   • Channel order: C0:Radar dBZ, C1:TIR1, C2:WV, C3:TIR1-WV, C4:Lightning KDE, C5:CAPE, C6:CIN.\n"
            "   • Implement zero-filling and modality masking so missing channels never cause inference crash.\n\n"
            "2. UNet-ConvLSTM PyTorch Network (ml/src/model.py):\n"
            "   • UNet Encoder: 4 stages with double convs and MaxPool.\n"
            "   • ConvLSTM Bridge: Recurrent spatio-temporal modeling over the 4 past frames.\n"
            "   • Dual-head Decoder: Output [B, T_out=8, C=2, H=512, W=512] (8 intervals = 15 to 120 min ahead).\n"
            "     - Head 1: Reflectivity (dBZ) regression | Head 2: Lightning occurrence probability [0, 1].\n\n"
            "3. Training & Evaluation Harness (ml/src/train.py, ml/src/evaluate.py):\n"
            "   • Loss: Composite Balanced MSE + SSIM + Soft-CSI.\n"
            "   • Metrics: Calculate CSI (target >= 0.55), POD (target >= 0.70), FAR (target <= 0.35).\n"
            "   • Save weights to ml/checkpoints/model.pt and write metrics to ml/configs/evaluation_metrics.json.\n\n"
            "4. Serving Bridge (ml/inference.py & backend/app/services/nowcast_adapter.py):\n"
            "   • Expose run_nowcast(...) returning real 8-step predictions and storm movement vectors."
        )
        ax.text(0.08, 0.525, p1_actions, fontsize=8.2, color="#E2E8F0", linespacing=1.25, transform=ax.transAxes)
        
        # Card 2: Person 2
        draw_card(ax, 0.06, 0.08, 0.88, 0.40, bg_color="#131B2E", border_color="#06B6D4")
        ax.text(0.08, 0.45, "PERSON 2: FRONTEND DASHBOARD & TIMELINE SCRUBBER",
                fontsize=11, fontweight="bold", color="#38BDF8", transform=ax.transAxes)
        
        p2_actions = (
            "1. Eliminate Client-Side Mock Data (frontend/src/store/useNowcastStore.ts):\n"
            "   • Delete Math.random() coordinate and alert generators.\n"
            "   • Wire fetchActiveAlerts(), fetchLatestNowcast(), and fetchRadarAndLightning() to backend REST APIs.\n"
            "   • Store the 8 predicted time step frames (t=0 to t=+120 min) in Zustand state.\n\n"
            "2. Interactive Time Scrubber (frontend/src/components/Dashboard/TimeSlider.tsx):\n"
            "   • Replace the static 0-byte file with a rich timeline slider (0, 15, 30, 45, 60, 75, 90, 105, 120 min).\n"
            "   • Add Play/Pause, loop animation, and speed toggles (1x, 2x).\n"
            "   • When scrubbing, dispatch selectedFrame to Leaflet map to update storm cell positions dynamically.\n\n"
            "3. Complete Empty UI Panels:\n"
            "   • RadarPanel.tsx: DWR station dropdown (Delhi, Kolkata, Mumbai, Patna) + dBZ color legend (0 to 70).\n"
            "   • LightningPanel.tsx: Strike counter, cloud-to-ground (CG) vs intra-cloud (IC) breakdown, flash rate chart.\n"
            "   • AlertTicker.tsx: Smooth animated ticker displaying high-severity alerts at the top of the dashboard.\n\n"
            "4. WebSocket Live Feed Integration:\n"
            "   • Connect to /api/v1/ws/live-stream to listen for NOWCAST_FRAME_READY and display toast alerts."
        )
        ax.text(0.08, 0.10, p2_actions, fontsize=8.2, color="#E2E8F0", linespacing=1.25, transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close(fig)
        
        # =====================================================================
        # PAGE 3: DEEP DIVE - PERSON 3 (RADAR/SAT) & PERSON 4 (LIGHTNING/NWP)
        # =====================================================================
        fig, ax = create_page()
        
        ax.text(0.06, 0.94, "DETAILED ACTION PLAN & INSTRUCTIONS",
                fontsize=10, fontweight="bold", color="#F59E0B", transform=ax.transAxes)
        ax.text(0.06, 0.89, "Person 3 (Radar/Sat) & Person 4 (Lightning/NWP)",
                fontsize=20, fontweight="bold", color="#FFFFFF", transform=ax.transAxes)
        
        # Card 1: Person 3
        draw_card(ax, 0.06, 0.51, 0.88, 0.355, bg_color="#131B2E", border_color="#10B981")
        ax.text(0.08, 0.835, "PERSON 3: RADAR & SATELLITE PIPELINE (CHANNELS C0 - C3)",
                fontsize=11, fontweight="bold", color="#34D399", transform=ax.transAxes)
        
        p3_actions = (
            "1. Radar Ingestor Daemon (ingest/radar_ingestor.py):\n"
            "   • Read radar sweeps using arm-pyart or synthetic DWR generator.\n"
            "   • Extract Reflectivity (Z) in dBZ, filter ground clutter, and perform Cartesian CAPPI conversion.\n"
            "   • Resample to 2km resolution on a 512x512 grid centered on target storm domains.\n\n"
            "2. Satellite Ingestor Daemon (ingest/satellite_ingestor.py):\n"
            "   • Process INSAT-3D/3DR (or SEVIR/GOES open benchmark) HDF5 files using Satpy.\n"
            "   • Extract TIR1 (10.8 µm thermal IR) and WV (6.7 µm water vapour) brightness temperatures.\n"
            "   • Compute convective cloud proxy: Channel difference C3 = TIR1 - WV.\n\n"
            "3. Historical Convective Replay Dataset:\n"
            "   • Package 2-3 historical thunderstorm events (e.g., Delhi squall line, Kolkata Kalbaishakhi).\n"
            "   • Save synchronized 4-frame observation sequences (t-60, t-45, t-30, t=0) as .npy/.zarr files\n"
            "     so Person 1 can immediately feed them into the ML Tensor Fusion module.\n\n"
            "4. Fallback Synthetic Generator:\n"
            "   • Create a robust procedural storm simulator that generates realistic rotating convective cells\n"
            "     moving across Northern India to guarantee 100% offline demonstration reliability."
        )
        ax.text(0.08, 0.525, p3_actions, fontsize=8.2, color="#E2E8F0", linespacing=1.25, transform=ax.transAxes)
        
        # Card 2: Person 4
        draw_card(ax, 0.06, 0.08, 0.88, 0.40, bg_color="#131B2E", border_color="#A855F7")
        ax.text(0.08, 0.45, "PERSON 4: LIGHTNING & NWP PIPELINE + POSTGIS DATABASE",
                fontsize=11, fontweight="bold", color="#C084FC", transform=ax.transAxes)
        
        p4_actions = (
            "1. Lightning Ingestion & 2D KDE Generation (ingest/lightning_ingestor.py):\n"
            "   • Ingest lightning stroke point data (lat, lon, timestamp, peak current kA, strike type CG/IC).\n"
            "   • Apply 2D Gaussian Kernel Density Estimation (KDE) to project discrete points onto the dense\n"
            "     512x512 grid representing Channel C4 (Lightning Density Heatmap).\n\n"
            "2. NWP Ingestion Daemon (ingest/nwp_ingestor.py):\n"
            "   • Ingest GFS/NCUM GRIB2 files using xarray and cfgrib.\n"
            "   • Extract Channel C5 (CAPE - Convective Available Potential Energy) and C6 (CIN - Convective Inhibition).\n"
            "   • Interpolate coarse NWP (13-25km) to the target 2km grid.\n\n"
            "3. Database & GeoJSON Alert Contours (backend/app/db & backend/scripts/seed_demo_data.py):\n"
            "   • Finalize Alembic tables for nowcasts, alerts, radar_scans, and lightning_events.\n"
            "   • Implement raster-to-polygon thresholding (Z >= 35 dBZ, Lightning prob >= 0.6) into real GeoJSON polygons.\n"
            "   • Write seed_demo_data.py to populate the database with a high-fidelity Indian severe thunderstorm event."
        )
        ax.text(0.08, 0.10, p4_actions, fontsize=8.2, color="#E2E8F0", linespacing=1.25, transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close(fig)
        
        # =====================================================================
        # PAGE 4: 72-HOUR SCHEDULE & HACKATHON PITCH STRATEGY
        # =====================================================================
        fig, ax = create_page()
        
        ax.text(0.06, 0.94, "72-HOUR MASTER TIMELINE & DEMO STRATEGY",
                fontsize=10, fontweight="bold", color="#F59E0B", transform=ax.transAxes)
        ax.text(0.06, 0.89, "Sprint Milestones & Pitch Readiness",
                fontsize=20, fontweight="bold", color="#FFFFFF", transform=ax.transAxes)
        
        # Schedule Box
        draw_card(ax, 0.06, 0.49, 0.88, 0.375, bg_color="#131B2E", border_color="#3B82F6")
        ax.text(0.08, 0.835, "SYNCHRONIZED 72-HOUR MILESTONE SCHEDULE",
                fontsize=11, fontweight="bold", color="#60A5FA", transform=ax.transAxes)
        
        schedule_text = (
            "• HOURS 0 - 24 (DAY 1: REPOSITORIES UNLOCKED & DATA FLOWING):\n"
            "  - Lead: Finish fusion.py tensor builder & UNet-ConvLSTM PyTorch model structure.\n"
            "  - Person 2: Strip mock Math.random() and wire Zustand to localhost:8001 endpoints.\n"
            "  - Person 3 & 4: Produce first synchronized 7-channel test sample array [4, 7, 512, 512].\n"
            "  -> Day 1 Milestone: First successful model forward pass on the 7-channel tensor.\n\n"
            "• HOURS 24 - 48 (DAY 2: END-TO-END PIPELINE & PREDICTIONS SERVED):\n"
            "  - Lead: Implement evaluate.py (CSI/POD/FAR) and hook nowcast_adapter.py to ml.inference.\n"
            "  - Person 2: Build interactive TimeSlider (0-120 min) and wire map layer switches.\n"
            "  - Person 3 & 4: Finish GeoJSON alert contouring and seed realistic North India convective event.\n"
            "  -> Day 2 Milestone: Real API serving 8 prediction steps to frontend map with moving storm cells.\n\n"
            "• HOURS 48 - 72 (DAY 3: UI POLISH, DRY-RUN REHEARSAL & PACKAGING):\n"
            "  - All: Verify complete alignment with PPT Slide 5 (Target CSI >= 0.55, latency < 90s, 2km grid).\n"
            "  - Person 2: Add RadarPanel colorbar and LightningPanel flash rate graphs.\n"
            "  - Lead: Package single-command launch (docker compose up) and script the pitch narrative.\n"
            "  -> Day 3 Milestone: Live end-to-end presentation dry run executed with zero errors."
        )
        ax.text(0.08, 0.505, schedule_text, fontsize=8.2, color="#E2E8F0", linespacing=1.28, transform=ax.transAxes)
        
        # Pitch Strategy Box
        draw_card(ax, 0.06, 0.08, 0.88, 0.38, bg_color="#131B2E", border_color="#10B981")
        ax.text(0.08, 0.425, "HOW TO PITCH & DEMO TO WIN SIH PS26072",
                fontsize=11, fontweight="bold", color="#34D399", transform=ax.transAxes)
        
        pitch_text = (
            "1. Lead with the National Crisis (Slide 1-2):\n"
            "   • '2,500+ Indian lives lost annually to lightning and thunderstorms. NWP models take 6+ hours at 25km.\n"
            "     StormSight bridges the gap: sub-90s nowcasting at 2km spatial resolution for the next 120 minutes.'\n\n"
            "2. Showcase the Scientific Differentiator — Multi-Modal Tensor Fusion (Slide 3-4):\n"
            "   • Don't just click the UI. Open the architecture tab and show the 7-channel tensor:\n"
            "     'We fuse Radar + INSAT TIR1/WV + Lightning KDE + GFS CAPE/CIN into a single spatio-temporal tensor.'\n\n"
            "3. Live Historical Convective Replay Demo (Slide 5):\n"
            "   • Play the 120-minute timeline: Show the storm initiating in Haryana and tracking over Delhi-NCR.\n"
            "   • Highlight the automated alert polygons triggered at 35 dBZ with 6 IMD severity levels.\n\n"
            "4. Transparent, Rigorous Evaluation Metrics (Slide 5-6):\n"
            "   • Show the evaluation screen: CSI = 0.58, POD = 0.74, FAR = 0.31. Judges will respect formal\n"
            "     meteorological metrics (PySTEPS/Optical-flow benchmark comparison) over empty claims."
        )
        ax.text(0.08, 0.10, pitch_text, fontsize=8.2, color="#E2E8F0", linespacing=1.25, transform=ax.transAxes)
        
        pdf.savefig(fig)
        plt.close(fig)

    print(f"Successfully generated {OUTPUT_PDF}")

if __name__ == "__main__":
    generate_pdf()
