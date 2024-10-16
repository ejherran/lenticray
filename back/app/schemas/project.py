# app/schemas/project.py

from pydantic import BaseModel, UUID4
from typing import Optional

class ProjectBase(BaseModel):
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area: Optional[float] = None
    depth: Optional[float] = None
    volume: Optional[float] = None
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: UUID4
    user_id: UUID4

    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    pass

class ProjectInDB(ProjectInDBBase):
    pass
