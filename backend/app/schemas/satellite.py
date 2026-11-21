from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SatelliteFrameRecord(BaseModel):
    id: str
    satellite_name: str
    channel: str
    acquisition_time: Optional[str] = None
    file_path: Optional[str] = None
    resolution_km: Optional[float] = 2.0


class SatelliteListResponse(BaseModel):
    frames: List[SatelliteFrameRecord] = Field(default_factory=list)
    count: int
