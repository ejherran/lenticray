from sqlalchemy import Column, String, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid
from enum import Enum as PyEnum
from app.db.base_class import Base

class TimeSpace(str, PyEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class StudyStatus(str, PyEnum):
    NEW = "NEW"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"

class Study(Base):
    __tablename__ = "studies"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    time_space = Column(Enum(TimeSpace), nullable=False)
    window_size = Column(Integer, nullable=False)
    status = Column(Enum(StudyStatus), nullable=False, default=StudyStatus.NEW)

    project = relationship("Project", back_populates="studies")
    dataset = relationship("Dataset", back_populates="studies")
