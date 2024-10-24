from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
from app.models.study import StudyStatus
import os
from app.core.config import settings
import shutil
from app.core.redis import redis_client
import json
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from io import StringIO
from loguru import logger
import pandas as pd

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

    # Verificar y actualizar el estado de cada estudio si es necesario
    studies_updated = False
    for study in studies:
        if study.status not in [StudyStatus.NEW, StudyStatus.TRAINED, StudyStatus.FAILED]:
            # Consultar el estado en Redis
            redis_status = redis_client.get(study.id)

            if redis_status is None:
                # Si no existe la clave en Redis, el estado es PENDING
                new_status = StudyStatus.PENDING
            else:
                redis_status = redis_status.decode('utf-8')
                if redis_status == 'RUNNING':
                    new_status = StudyStatus.TRAINING
                elif redis_status == 'FINISHED':
                    new_status = StudyStatus.TRAINED
                elif redis_status == 'FAILED':
                    new_status = StudyStatus.FAILED
                else:
                    new_status = study.status  # Mantener el estado actual si es desconocido

            # Si el nuevo estado es diferente, actualizarlo
            if new_status != study.status:
                study.status = new_status
                studies_updated = True
        
        study.dataset_name = crud.dataset.get(db=db, id=study.dataset_id).name

    if studies_updated:
        db.commit()  # Confirmar los cambios en la base de datos

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

    # Evitar eliminación si el estudio está en PENDING o TRAINING
    if study.status in [StudyStatus.PENDING, StudyStatus.TRAINING]:
        raise HTTPException(status_code=400, detail="No se puede eliminar un estudio en estado PENDING o TRAINING")

    # Eliminar key de Redis
    redis_client.delete(study.id)

    # Eliminar el directorio del estudio
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))

    if os.path.exists(study_dir):
        shutil.rmtree(study_dir)

    study = crud.study.remove(db=db, id=study_id)

    return study

@router.post("/{study_id}/start_training", status_code=status.HTTP_201_CREATED)
def start_study_training(
    *,
    db: Session = Depends(deps.get_db),
    study_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Iniciar el entrenamiento de un estudio.
    """
    # Obtener el estudio
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    # Verificar permisos
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para iniciar este estudio")

    # Verificar estado
    if study.status != StudyStatus.NEW:
        raise HTTPException(status_code=400, detail="El estudio ya fue entrenado o está en proceso de entrenamiento")

    # Preparar los datos para la cola
    user_data_dir = os.path.join("user", str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))

    job_data = {
        'id': study.id,
        'payload': {
            'id': study.id,
            'work_dir': study_dir,
            'window_size': study.window_size,
            'temporal_space': study.time_space,
            'target_body': project.name,
            'mode': 'TRAIN'
        }
    }

    # Poner el trabajo en la cola de Redis
    try:
        redis_client.lpush('jobs', json.dumps(job_data))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al conectar con Redis")

    # Actualizar el estado del estudio a 'TRAINING'
    study_update = schemas.StudyUpdate(status=StudyStatus.PENDING)
    study = crud.study.update(db=db, db_obj=study, obj_in=study_update)

    return {"message": "Estudio en proceso de entrenamiento"}


@router.get("/{study_id}/download_results", response_class=StreamingResponse)
def download_study_results(
    *,
    db: Session = Depends(deps.get_db),
    study_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> StreamingResponse:
    """
    Descargar los resultados del estudio en formato CSV.
    """
    # Verificar que el estudio existe
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    # Verificar permisos
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")

    # Verificar que el estudio está en estado TRAINED
    if study.status != StudyStatus.TRAINED:
        raise HTTPException(status_code=400, detail="El estudio aún no ha sido entrenado")

    columns = ["eutrophication_level", "chemical_conditions", "physical_conditions", "additional_conditions"]

    # Construir las rutas a los archivos
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    fuzzy_file = os.path.join(study_dir, "fuzzy.parquet")
    fuzzy_tags_file = os.path.join(study_dir, "fuzzy_tags.parquet")

    # Verificar que los archivos existen
    if not os.path.exists(fuzzy_file) or not os.path.exists(fuzzy_tags_file):
        raise HTTPException(status_code=404, detail="Archivos de resultados no encontrados")

    # Cargar los dataframes
    try:
        df_fuzzy = pd.read_parquet(fuzzy_file)
        df_fuzzy_tags = pd.read_parquet(fuzzy_tags_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al leer los archivos de resultados")

    # Seleccionar las columnas disponibles
    available_columns = [col for col in columns if col in df_fuzzy.columns]
    if not available_columns:
        raise HTTPException(status_code=400, detail="No hay columnas disponibles en los resultados")

    # Crear columnas de tags
    for col in available_columns:
        if col in df_fuzzy_tags.columns:
            df_fuzzy[col + "_tag"] = df_fuzzy_tags[col]
        else:
            # Si la columna de tag no existe, podemos omitirla o manejar el error
            pass

    # Unificar las columnas disponibles
    result_columns = []
    for col in available_columns:
        result_columns.append(col)
        if col + "_tag" in df_fuzzy.columns:
            result_columns.append(col + "_tag")

    # Seleccionar las columnas finales
    df_result = df_fuzzy[result_columns]

    # Convertir el dataframe a CSV en memoria
    csv_buffer = StringIO()
    df_result.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Retornar el CSV como respuesta de descarga
    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=train_{study.id}_results.csv"}
    )

@router.get("/{study_id}/results", response_class=JSONResponse)
def get_study_results(
    *,
    db: Session = Depends(deps.get_db),
    study_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener los resultados del estudio en formato JSON.
    """
    # Verificar que el estudio existe
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")

    # Verificar permisos
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")

    # Verificar que el estudio está en estado TRAINED
    if study.status != StudyStatus.TRAINED:
        raise HTTPException(status_code=400, detail="El estudio aún no ha sido entrenado")

    # Definir los posibles nombres de columnas
    columns = ["eutrophication_level", "chemical_conditions", "physical_conditions", "additional_conditions"]

    # Construir las rutas a los archivos
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    fuzzy_file = os.path.join(study_dir, "fuzzy.parquet")
    fuzzy_tags_file = os.path.join(study_dir, "fuzzy_tags.parquet")

    # Verificar que los archivos existen
    if not os.path.exists(fuzzy_file) or not os.path.exists(fuzzy_tags_file):
        raise HTTPException(status_code=404, detail="Archivos de resultados no encontrados")

    # Cargar los dataframes
    try:
        df_fuzzy = pd.read_parquet(fuzzy_file)
        df_fuzzy_tags = pd.read_parquet(fuzzy_tags_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al leer los archivos de resultados")

    # Seleccionar las columnas disponibles
    available_columns = [col for col in columns if col in df_fuzzy.columns]
    if not available_columns:
        raise HTTPException(status_code=400, detail="No hay columnas disponibles en los resultados")

    # Crear columnas de tags
    for col in available_columns:
        if col in df_fuzzy_tags.columns:
            df_fuzzy[col + "_tag"] = df_fuzzy_tags[col]

    # Unificar las columnas disponibles
    result_columns = []
    for col in available_columns:
        result_columns.append(col)
        if col + "_tag" in df_fuzzy.columns:
            result_columns.append(col + "_tag")

    # Seleccionar las columnas finales
    df_result = df_fuzzy[result_columns]

    # Convertir el dataframe a JSON
    result_json = df_result.to_dict(orient="records")

    # Retornar el JSON
    return JSONResponse(content=result_json)