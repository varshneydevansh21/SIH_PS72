from pydantic import BaseModel


class LatLon(BaseModel):
    lat: float
    lon: float


class BBox(BaseModel):
    lat_min: float
    lon_min: float
    lat_max: float
    lon_max: float


class ModelInfo(BaseModel):
    name: str
    version: str
