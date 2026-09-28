"""Satellite frame metadata model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base

class SatelliteFrame(Base):
    __tablename__ = "satellite_frames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    satellite_name = Column(String, nullable=False, index=True) # INSAT-3D, INSAT-3DR
    channel = Column(String, nullable=False) # e.g., TIR1, MIR, VIS
    scan_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    file_path = Column(String, nullable=False)
    bbox = Column(Geometry('POLYGON', srid=4326), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
