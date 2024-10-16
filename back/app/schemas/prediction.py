from typing import Optional
from pydantic import BaseModel
from enum import Enum

class PredictionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class PredictionBase(BaseModel):
    name: str
    window_size: int
    amount: int

class PredictionCreate(PredictionBase):
    study_id: str

class PredictionUpdate(BaseModel):
    status: Optional[PredictionStatus] = None

class PredictionInDBBase(PredictionBase):
    id: str
    study_id: str
    status: PredictionStatus

    class Config:
        from_attributes = True

class Prediction(PredictionInDBBase):
    pass
