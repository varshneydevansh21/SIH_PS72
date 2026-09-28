"""Lightning event observation model."""
import uuid
from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import Base

class LightningEvent(Base):
    __tablename__ = "lightning_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    event_time = Column(DateTime(timezone=True), nullable=False, index=True)
    
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    current_ka = Column(Float, nullable=True)
    polarity = Column(Integer, nullable=True) # 1 for positive, -1 for negative
