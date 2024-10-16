# app/schemas/variable.py

from pydantic import BaseModel

class VariableBase(BaseModel):
    id: str
    name: str
    description: str
    unit: str

    class Config:
        from_attributes = True


class Variable(VariableBase):
    pass
