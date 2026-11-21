from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class LightningStroke(BaseModel):
    id: str
    event_time: Optional[str] = None
    lat: float
    lon: float
    current_ka: Optional[float] = None
    polarity: Optional[str] = None
    strike_type: Optional[str] = "CG"


class LightningResponse(BaseModel):
    strokes: List[LightningStroke] = Field(default_factory=list)
    count: int


class LightningDensityResponse(BaseModel):
    bbox: Dict[str, float]
    density_grid: List[List[float]] = Field(default_factory=list)
    max_density: Optional[float] = 0.0
    message: Optional[str] = None
