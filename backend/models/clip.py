from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Clip(Base):
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    viral_score = Column(Float, nullable=True)
    style = Column(String, default="simple")  # simple, zoom, jumpcuts
    output_path = Column(String, nullable=True)
    transcript_segment = Column(Text, nullable=True)
    clip_metadata = Column(JSON, nullable=True)  # Store additional info like emotions, hooks, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video = relationship("Video", back_populates="clips")
