"""Radar scan metadata model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base

class RadarScan(Base):
    __tablename__ = "radar_scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    station_id = Column(String, nullable=False, index=True)
    scan_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Path to the raw or processed NetCDF/HDF5 file on disk/cloud
    file_path = Column(String, nullable=False)
    
    # Bounding box of the radar coverage
    bbox = Column(Geometry('POLYGON', srid=4326), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
