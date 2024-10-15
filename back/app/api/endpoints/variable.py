# app/api/endpoints/variable.py

from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Variable])
def read_variables(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Obtener la lista de variables disponibles.
    """
    variables = db.query(models.Variable).offset(skip).limit(limit).all()
    return variables

