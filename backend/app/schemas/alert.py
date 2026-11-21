from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AlertItem(BaseModel):
    id: str
    nowcast_id: Optional[str] = None
    alert_type: str
    severity: str
    issue_time: Optional[str] = None
    valid_until: Optional[str] = None
    message: str
    centroid_lat: float
    centroid_lon: float
    radius_km: Optional[float] = 30.0
    probability: Optional[float] = None
    hazards: Optional[Dict[str, Any]] = None


class AlertListResponse(BaseModel):
    alerts: List[AlertItem] = Field(default_factory=list)
    count: int
