"""
SIH PS072 - Doppler Weather Radar (DWR) Data Client

Fetches radar reflectivity data from IMD's Doppler Weather Radar network.
Supports both API-based retrieval and local file ingestion (for offline dev).

IMD operates ~37 DWR stations. This client handles:
  - Volume scan data (reflectivity, radial velocity, spectrum width)
  - PPI (Plan Position Indicator) sweeps at multiple elevation angles
  - Compositing multiple radar sites into a unified grid

File formats supported: HDF5, NetCDF, raw binary sweep files.
"""
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

import logging
import httpx
import numpy as np

logger = logging.getLogger(__name__)

from app.core.config import get_settings
from app.ingestion.base import BaseIngestor

# Py-ART is the standard for radar data in meteorology
# Import guarded so the app still starts without it during early dev
try:
    import pyart
    HAS_PYART = True
except ImportError:
    HAS_PYART = False
    logger.warning("arm-pyart not installed — radar processing will be limited")


class DWRClient(BaseIngestor):
    """
    Doppler Weather Radar ingestor.
    Fetches volume scan data and converts it to a normalised grid.
    """

    def __init__(self):
        super().__init__(source_name="IMD_DWR_Radar")
        self.settings = get_settings()
        api_url = getattr(self.settings, "imd_radar_api_url", "") or "http://localhost:8001"
        api_key = getattr(self.settings, "imd_radar_api_key", "")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = httpx.AsyncClient(
            base_url=api_url,
            timeout=60.0,
            headers=headers,
        )
        from app.ingestion.radar.processor import RadarProcessor
        self.processor = RadarProcessor(
            target_h=self.settings.pilot_grid_h,
            target_w=self.settings.pilot_grid_w,
        )

    async def fetch(self) -> Any:
        app_env = getattr(self.settings, "app_env", "development")
        api_url = getattr(self.settings, "imd_radar_api_url", "")
        if app_env == "development" or not api_url:
            return await self._fetch_local_sample()

        try:
            response = await self._client.get(
                "/latest",
                params={"format": "hdf5", "product": "reflectivity"},
            )
            response.raise_for_status()
            logger.debug("Fetched {} bytes from DWR API", len(response.content))
            return response.content

        except httpx.HTTPError as e:
            logger.error("DWR API request failed: {}", e)
            raise

    async def _fetch_local_sample(self) -> Optional[bytes]:
        """Load a sample radar file from local data directory for offline dev."""
        sample_dir = Path("data/raw/radar")
        samples = list(sample_dir.glob("*.hdf5")) + list(sample_dir.glob("*.nc"))

        if not samples:
            logger.warning(
                "No sample radar files found in {}. "
                "Run `python scripts/download_sample_data.py` to fetch test data.",
                sample_dir,
            )
            return None

        latest = max(samples, key=lambda p: p.stat().st_mtime)
        logger.info("Loading local radar sample: {}", latest.name)
        return latest.read_bytes()

    async def process(self, raw_data: Any) -> Dict[str, Any]:
        """
        Process raw radar bytes into a normalised reflectivity grid.

        Steps:
            1. Parse HDF5/NetCDF volume scan with Py-ART
            2. Apply quality control (clutter removal, dealiasing)
            3. Grid to a Cartesian coordinate system
            4. Extract the reflectivity field as a numpy array

        Returns:
            Dictionary with:
                - "reflectivity": np.ndarray of shape (n_z, n_y, n_x)
                - "metadata": dict with timestamp, radar site, resolution, etc.
        """
        if not HAS_PYART:
            logger.warning("Py-ART unavailable — returning raw data passthrough")
            return {"reflectivity": None, "metadata": {"raw_bytes": len(raw_data)}}

        # Py-ART expects a file — write to temp, read, then clean up
        # In production, you'd use an in-memory buffer or stream
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".hdf5", delete=True) as tmp:
            tmp.write(raw_data)
            tmp.flush()

            # Run CPU-bound radar processing in a thread pool
            radar = await asyncio.to_thread(pyart.io.read, tmp.name)

        # --- Quality Control ---
        # (Placeholder: Add clutter filters, velocity dealiasing here)

        # --- Grid the data to Cartesian (250m resolution, 500km range) ---
        grid = await asyncio.to_thread(
            pyart.map.grid_from_radars,
            (radar,),
            grid_shape=(20, 401, 401),            # (z, y, x) levels
            grid_limits=(
                (500, 15000),                      # altitude: 0.5 to 15 km
                (-200000, 200000),                 # y: ±200 km
                (-200000, 200000),                 # x: ±200 km
            ),
            fields=["reflectivity"],
        )

        reflectivity = grid.fields["reflectivity"]["data"]

        metadata = {
            "radar_name": radar.metadata.get("instrument_name", "unknown"),
            "scan_time": str(radar.time["units"]),
            "n_sweeps": radar.nsweeps,
            "grid_shape": list(reflectivity.shape),
            "max_reflectivity_dbz": float(np.nanmax(reflectivity)),
        }

        logger.info(
            "Radar processed: {} | max dBZ={:.1f} | shape={}",
            metadata["radar_name"],
            metadata["max_reflectivity_dbz"],
            metadata["grid_shape"],
        )

        return {"reflectivity": reflectivity, "metadata": metadata}

    async def close(self):
        """Clean up the HTTP client."""
        await self._client.aclose()
