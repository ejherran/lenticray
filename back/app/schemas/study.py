from typing import Optional
from pydantic import BaseModel
from enum import Enum

class TimeSpace(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"

class StudyStatus(str, Enum):
    NEW = "NEW"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    PENDING = "PENDING"
    FAILED = "FAILED"

class StudyBase(BaseModel):
    name: str
    time_space: TimeSpace
    window_size: int

class StudyCreate(StudyBase):
    project_id: str
    dataset_id: str

class StudyUpdate(BaseModel):
    name: Optional[str] = None
    time_space: Optional[TimeSpace] = None
    window_size: Optional[int] = None
    status: Optional[StudyStatus] = None

class StudyInDBBase(StudyBase):
    id: str
    project_id: str
    dataset_id: str
    status: StudyStatus

    class Config:
        from_attributes = True

class Study(StudyInDBBase):
    pass
