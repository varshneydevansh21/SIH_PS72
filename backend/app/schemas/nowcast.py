from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StormCenter(BaseModel):
    lat: float
    lon: float


class ForecastPosition(BaseModel):
    minutes_ahead: int
    lat: float
    lon: float
    probability: float


class HazardDetails(BaseModel):
    lightning: Optional[Dict[str, Any]] = None
    hail: Optional[Dict[str, Any]] = None
    wind_gust_kmh: Optional[int] = None


class StormMotion(BaseModel):
    bearing_deg: float
    speed_kmh: float


class StormCell(BaseModel):
    cell_id: str
    center: StormCenter
    radius_km: float
    severity: str
    probability: float
    max_reflectivity_dbz: Optional[float] = None
    hazards: Optional[HazardDetails] = None
    motion: Optional[StormMotion] = None
    forecast_positions: Optional[List[ForecastPosition]] = None


class NowcastResponse(BaseModel):
    nowcast_id: str
    issued_at: str
    valid_until: str
    horizon_minutes: Optional[int] = 120
    interval_minutes: Optional[int] = 15
    timesteps: Optional[List[int]] = [15, 30, 45, 60, 75, 90, 105, 120]
    cells: List[StormCell] = Field(default_factory=list)
    model: Optional[Dict[str, Any]] = None
    data_sources_used: Optional[List[str]] = None


class NowcastRecord(BaseModel):
    cell_id: str
    run_time: Optional[str] = None
    lead_time_minutes: int
    severity: str
    probability: float
    details: Optional[Dict[str, Any]] = None
    center: StormCenter
    radius_km: float


class NowcastListResponse(BaseModel):
    nowcasts: List[NowcastRecord]
    count: int
