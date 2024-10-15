from sqlalchemy import Column, String, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from app.db.base_class import Base

class PredictionStatus(str, PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    study_id = Column(String, ForeignKey("studies.id"), nullable=False)
    name = Column(String, nullable=False)
    window_size = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(Enum(PredictionStatus), nullable=False, default=PredictionStatus.PENDING)

    study = relationship("Study", back_populates="predictions")
