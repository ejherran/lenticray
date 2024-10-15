# app/api/endpoints/project.py

import os
import shutil
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=schemas.Project)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    project_in: schemas.ProjectCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crear un nuevo proyecto.
    """
    project = crud.project.create_with_owner(db=db, obj_in=project_in, user_id=current_user.id)

    # Gestión de directorios: Crear directorio de proyecto

    user_data_dir = os.path.join(settings.USER_DATA, current_user.id)
    project_dir = os.path.join(user_data_dir, project.id)
    os.makedirs(project_dir, exist_ok=True)

    return project

@router.get("/", response_model=List[schemas.Project])
def read_projects(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener proyectos del usuario actual.
    """
    projects = crud.project.get_multi_by_owner(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=schemas.Project)
def read_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener un proyecto por ID.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este proyecto")
    return project

@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    project_in: schemas.ProjectUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Actualizar un proyecto.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para actualizar este proyecto")
    project = crud.project.update(db=db, db_obj=project, obj_in=project_in)
    return project

@router.delete("/{project_id}", response_model=schemas.Project)
def delete_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Eliminar un proyecto.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para eliminar este proyecto")
    project = crud.project.remove(db=db, id=project_id)

    # Gestión de directorios: Eliminar directorio de proyecto
    user_data_dir = os.path.join(settings.USER_DATA, current_user.id)
    project_dir = os.path.join(user_data_dir, project_id)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)

    return project
