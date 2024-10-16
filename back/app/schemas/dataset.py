# app/schemas/dataset.py

from pydantic import BaseModel, UUID4
from typing import List, Dict, Any
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
        from_attributes = True

class Dataset(DatasetInDBBase):
    pass

class DatasetPage(BaseModel):
    data: List[Dict[str, Any]]
    page_size: int
    page_number: int
    total_rows: int
    total_pages: int


class DatasetPageUpdate(BaseModel):
    page_size: int
    page_number: int
    data: List[Dict[str, Any]]