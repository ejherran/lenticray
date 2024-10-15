from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
import os
from app.core.config import settings
import shutil

router = APIRouter()

@router.post("/", response_model=schemas.Study)
def create_study(
    *,
    db: Session = Depends(deps.get_db),
    study_in: schemas.StudyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crear un nuevo estudio.
    """
    project = crud.project.get(db=db, id=study_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este proyecto")

    dataset = crud.dataset.get(db=db, id=study_in.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")
    if dataset.project_id != project.id:
        raise HTTPException(status_code=400, detail="El dataset no pertenece al proyecto indicado")

    study = crud.study.create_with_project(db=db, obj_in=study_in, project_id=project.id)

    # Crear directorio del estudio dentro del proyecto
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    os.makedirs(study_dir, exist_ok=True)

    # Copiar el archivo parquet del dataset al directorio del estudio
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")
    study_dataset_file = os.path.join(study_dir, "data.parquet")
    if not os.path.exists(dataset_file):
        raise HTTPException(status_code=404, detail="Archivo de dataset no encontrado")
    shutil.copy2(dataset_file, study_dataset_file)

    return study

@router.get("/", response_model=List[schemas.Study])
def read_studies(
    db: Session = Depends(deps.get_db),
    project_id: str = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener estudios de un proyecto.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este proyecto")

    studies = crud.study.get_multi_by_project(db=db, project_id=project_id, skip=skip, limit=limit)
    return studies

@router.get("/{study_id}", response_model=schemas.Study)
def read_study(
    *,
    db: Session = Depends(deps.get_db),
    study_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener un estudio por ID.
    """
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")

    return study

@router.put("/{study_id}", response_model=schemas.Study)
def update_study(
    *,
    db: Session = Depends(deps.get_db),
    study_id: str,
    study_in: schemas.StudyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Actualizar un estudio (solo si está en estado NEW).
    """
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    if study.status != "NEW":
        raise HTTPException(status_code=400, detail="El estudio no puede ser editado en este estado")

    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para actualizar este estudio")

    study = crud.study.update(db=db, db_obj=study, obj_in=study_in)
    return study

@router.delete("/{study_id}", response_model=schemas.Study)
def delete_study(
    *,
    db: Session = Depends(deps.get_db),
    study_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Eliminar un estudio.
    """
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para eliminar este estudio")

    # Eliminar el directorio del estudio
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))

    if os.path.exists(study_dir):
        shutil.rmtree(study_dir)

    study = crud.study.remove(db=db, id=study_id)

    return study
