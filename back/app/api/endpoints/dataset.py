# app/api/endpoints/dataset.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
import os
import pandas as pd
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=schemas.Dataset)
def create_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_in: schemas.DatasetCreate,
    project_id: str = Query(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crear un nuevo dataset en un proyecto con las variables seleccionadas.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este proyecto")

    dataset = crud.dataset.create_with_project(db=db, obj_in=dataset_in, project_id=project_id)

    # Crear dataframe vacío y guardarlo en formato Parquet
    columns = ["Water Body", "Sample Date"] + dataset_in.variable_ids
    df = pd.DataFrame(columns=columns)

    # Asignar "Water Body" del nombre del proyecto
    df["Water Body"] = [project.name]
    # "Sample Date" se deja vacío inicialmente

    # Guardar el DataFrame en el directorio del proyecto
    user_data_dir = os.path.join(settings.USER_DATA, current_user.id)
    project_dir = os.path.join(user_data_dir, project_id)
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")

    df.to_parquet(dataset_file, index=False)

    return dataset

@router.get("/", response_model=List[schemas.Dataset])
def read_datasets(
    db: Session = Depends(deps.get_db),
    project_id: str = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener datasets de un proyecto.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este proyecto")

    datasets = crud.dataset.get_multi_by_project(db=db, project_id=project_id, skip=skip, limit=limit)
    return datasets

@router.get("/{dataset_id}", response_model=schemas.Dataset)
def read_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener un dataset por ID.
    """
    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este dataset")

    return dataset

@router.put("/{dataset_id}", response_model=schemas.Dataset)
def update_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    dataset_in: schemas.DatasetUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Actualizar el nombre de un dataset.
    """
    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para actualizar este dataset")

    dataset = crud.dataset.update(db=db, db_obj=dataset, obj_in=dataset_in)
    return dataset

@router.delete("/{dataset_id}", response_model=schemas.Dataset)
def delete_dataset(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Eliminar un dataset.
    """
    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para eliminar este dataset")

    # Eliminar el archivo Parquet
    user_data_dir = os.path.join(settings.USER_DATA, current_user.id)
    project_dir = os.path.join(user_data_dir, project.id)
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")

    if os.path.exists(dataset_file):
        os.remove(dataset_file)

    dataset = crud.dataset.remove(db=db, id=dataset_id)

    return dataset
