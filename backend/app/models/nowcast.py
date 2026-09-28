"""Nowcast output model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base

class Nowcast(Base):
    __tablename__ = "nowcasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    run_time = Column(DateTime(timezone=True), nullable=False, index=True)
    lead_time_minutes = Column(Integer, nullable=False) # e.g., 30, 60, 90, 120
    
    # Store the predicted area of the storm
    affected_area = Column(Geometry('POLYGON', srid=4326), nullable=True)
    
    # Could be a single max intensity value or a categorical string
    storm_intensity_class = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    
    # Store arbitrary extra model outputs (e.g., confidence intervals, grid paths)
    details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
