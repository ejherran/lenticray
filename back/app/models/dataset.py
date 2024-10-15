# app/models/dataset.py

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid
from datetime import datetime
from app.models.dataset_variable import dataset_variable

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rows = Column(Integer, default=0)

    project = relationship("Project", back_populates="datasets")
    variables = relationship("Variable", secondary=dataset_variable, backref="datasets")
    studies = relationship("Study", back_populates="dataset", cascade="all, delete-orphan")
