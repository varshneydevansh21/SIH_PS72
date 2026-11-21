from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class RadarBBox(BaseModel):
    min_lat: Optional[float] = None
    min_lon: Optional[float] = None
    max_lat: Optional[float] = None
    max_lon: Optional[float] = None


class RadarScanRecord(BaseModel):
    id: str
    station_id: str
    scan_time: Optional[str] = None
    file_path: Optional[str] = None
    bbox: Optional[RadarBBox] = None


class RadarListResponse(BaseModel):
    scans: List[RadarScanRecord] = Field(default_factory=list)
    count: int


class StationRadarResponse(BaseModel):
    station_id: str
    scans: List[RadarScanRecord] = Field(default_factory=list)
