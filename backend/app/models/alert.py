"""Alert model based on Nowcasts."""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from app.models.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nowcast_id = Column(UUID(as_uuid=True), ForeignKey("nowcasts.id"), nullable=False, index=True)
    
    alert_type = Column(String, nullable=False) # e.g., "THUNDERSTORM", "LIGHTNING", "SQUALL"
    severity = Column(String, nullable=False)   # e.g., "YELLOW", "ORANGE", "RED"
    
    issue_time = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    
    alert_area = Column(Geometry('POLYGON', srid=4326), nullable=True)
    message = Column(String, nullable=False)
    
    nowcast = relationship("Nowcast")
