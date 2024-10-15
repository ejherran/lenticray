# app/schemas/dataset.py

from pydantic import BaseModel, UUID4
from typing import List
from datetime import datetime
from app.schemas.variable import Variable

class DatasetBase(BaseModel):
    name: str

class DatasetCreate(DatasetBase):
    variable_ids: List[str]  # List of selected variable IDs

class DatasetUpdate(BaseModel):
    name: str

class DatasetInDBBase(DatasetBase):
    id: UUID4
    project_id: UUID4
    date: datetime
    rows: int
    variables: List[Variable] = []  # List of Variable objects

    class Config:
        orm_mode = True

class Dataset(DatasetInDBBase):
    pass
