# app/models/variable.py

from sqlalchemy import Column, String
from app.db.base_class import Base

class Variable(Base):
    __tablename__ = "variables"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    unit = Column(String, nullable=False)
