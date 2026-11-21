from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class NWPRunRecord(BaseModel):
    id: str
    model_name: str
    run_time: Optional[str] = None
    forecast_hour: int
    variable_name: str
    file_path: Optional[str] = None


class NWPListResponse(BaseModel):
    runs: List[NWPRunRecord] = Field(default_factory=list)
    count: int
