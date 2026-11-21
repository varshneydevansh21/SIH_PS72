"""Application configuration loaded from environment variables.

Adapted from PS 070 CycloneWatch config for PS 072 Thunderstorm Nowcasting.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -- Database ----------------------------------------------------------
    database_url: str = (
        "sqlite+aiosqlite:///nowcast.db"
    )
    database_sync_url: str = (
        "sqlite:///nowcast.db"
    )

    # -- Application -------------------------------------------------------
    app_env: str = "development"
    debug: bool = True
    api_version: str = "v1"

    # -- CORS --------------------------------------------------------------
    cors_origins: str = "*"

    # -- Data paths --------------------------------------------------------
    data_root: str = "data"
    radar_data_dir: str = "data/raw/radar"
    lightning_data_dir: str = "data/raw/lightning"
    satellite_data_dir: str = "data/raw/satellite"
    nwp_data_dir: str = "data/raw/nwp"

    # -- Atmospheric Data Credentials & APIs ------------------------------
    imd_radar_api_url: str = ""
    imd_radar_api_key: str = ""
    mosdac_username: str = ""
    mosdac_password: str = ""

    # -- Pilot Domain Geometry (Delhi NCR) ---------------------------------
    pilot_domain_name: str = "Delhi NCR"
    pilot_center_lat: float = 28.6139
    pilot_center_lon: float = 77.2090
    pilot_grid_h: int = 512
    pilot_grid_w: int = 512
    pilot_grid_res_km: float = 2.0
    pilot_bbox_lat_min: float = 24.0
    pilot_bbox_lat_max: float = 33.2
    pilot_bbox_lon_min: float = 72.0
    pilot_bbox_lon_max: float = 82.5

    # -- ML ----------------------------------------------------------------
    ml_package_path: str = "/ml"
    ml_force_stub: bool = False

    # -- Redis (caching + pub/sub for real-time push) ----------------------
    redis_url: str = "redis://localhost:6379/0"

    # -- Kafka / Redpanda (streaming ingest) -------------------------------
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_radar_topic: str = "radar.scans"
    kafka_lightning_topic: str = "lightning.strokes"

    # -- Nowcasting --------------------------------------------------------
    nowcast_horizon_minutes: int = 120
    nowcast_interval_minutes: int = 15
    alert_threshold_probability: float = 0.60

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
