"""NWP (Numerical Weather Prediction) model run metadata."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base

class NWPRun(Base):
    __tablename__ = "nwp_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_name = Column(String, nullable=False, index=True) # e.g., IMD-GFS, NCUM
    run_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    file_path = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
