from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
import os
from app.core.config import settings
from app.models.prediction import PredictionStatus
from app.models.study import StudyStatus
from app.core.redis import redis_client
import json
import pandas as pd
from fastapi.responses import StreamingResponse
from io import StringIO
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/", response_model=schemas.Prediction, status_code=status.HTTP_201_CREATED)
def create_prediction(
    *,
    db: Session = Depends(deps.get_db),
    prediction_in: schemas.PredictionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Crear una nueva predicción.
    """
    # Verificar que el estudio existe y está en estado TRAINED
    study = crud.study.get(db=db, id=prediction_in.study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    if study.status != StudyStatus.TRAINED:
        raise HTTPException(status_code=400, detail="El estudio no está en estado TRAINED")
    # Verificar permisos
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")
    # Crear la predicción
    prediction = crud.prediction.create_with_study(
        db=db, obj_in=prediction_in, study_id=study.id
    )
    # Encolar el trabajo en Redis
    user_data_dir = os.path.join("user", str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    job_data = {
        'id': prediction.id,
        'payload': {
            'id': prediction.id,
            'work_dir': study_dir,
            'window_size': prediction.window_size,
            'amount': prediction.amount,
            'output_tag': prediction.id,
            'mode': 'PREDICT'
        }
    }
    try:
        redis_client.lpush('jobs', json.dumps(job_data))
    except Exception as e:
        # Si falla la conexión a Redis, eliminamos la predicción creada
        crud.prediction.remove(db=db, id=prediction.id)
        raise HTTPException(status_code=500, detail="Error al conectar con Redis")

    return prediction

@router.get("/", response_model=List[schemas.Prediction])
def read_predictions(
    db: Session = Depends(deps.get_db),
    study_id: str = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener predicciones de un estudio.
    """
    study = crud.study.get(db=db, id=study_id)
    if not study:
        raise HTTPException(status_code=404, detail="Estudio no encontrado")
    # Verificar permisos
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este estudio")
    predictions = crud.prediction.get_multi_by_study(
        db=db, study_id=study_id, skip=skip, limit=limit
    )

    # Verificar y actualizar el estado de cada predicción si es necesario
    predictions_updated = False
    for prediction in predictions:
        if prediction.status not in [PredictionStatus.COMPLETE, PredictionStatus.FAILED]:
            # Consultar el estado en Redis
            redis_status = redis_client.get(prediction.id)
            if redis_status is None:
                # Si no existe la clave en Redis, el estado es PENDING
                new_status = PredictionStatus.PENDING
            else:
                redis_status = redis_status.decode('utf-8')
                if redis_status == 'RUNNING':
                    new_status = PredictionStatus.RUNNING
                elif redis_status == 'FINISHED':
                    new_status = PredictionStatus.COMPLETE
                elif redis_status == 'FAILED':
                    new_status = PredictionStatus.FAILED
                else:
                    new_status = prediction.status  # Mantener el estado actual si es desconocido

            # Si el nuevo estado es diferente, actualizarlo
            if new_status != prediction.status:
                prediction.status = new_status
                predictions_updated = True

    if predictions_updated:
        db.commit()  # Confirmar los cambios en la base de datos

    return predictions

@router.get("/{prediction_id}", response_model=schemas.Prediction)
def read_prediction(
    *,
    db: Session = Depends(deps.get_db),
    prediction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener una predicción por ID.
    """
    prediction = crud.prediction.get(db=db, id=prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    # Verificar permisos
    study = crud.study.get(db=db, id=prediction.study_id)
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a esta predicción")

    # Verificar y actualizar el estado si es necesario
    if prediction.status not in [PredictionStatus.COMPLETE, PredictionStatus.FAILED]:
        # Consultar el estado en Redis
        redis_key = f"prediction:{prediction.id}"
        redis_status = redis_client.get(redis_key)
        if redis_status is None:
            # Si no existe la clave en Redis, el estado es PENDING
            new_status = PredictionStatus.PENDING
        else:
            redis_status = redis_status.decode('utf-8')
            if redis_status == 'RUNNING':
                new_status = PredictionStatus.RUNNING
            elif redis_status == 'FINISHED':
                new_status = PredictionStatus.COMPLETE
            elif redis_status == 'FAILED':
                new_status = PredictionStatus.FAILED
            else:
                new_status = prediction.status  # Mantener el estado actual si es desconocido

        # Si el nuevo estado es diferente, actualizarlo
        if new_status != prediction.status:
            prediction.status = new_status
            db.commit()
            db.refresh(prediction)

    return prediction

@router.delete("/{prediction_id}", response_model=schemas.Prediction)
def delete_prediction(
    *,
    db: Session = Depends(deps.get_db),
    prediction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Eliminar una predicción.
    """
    prediction = crud.prediction.get(db=db, id=prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    # Verificar permisos
    study = crud.study.get(db=db, id=prediction.study_id)
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para eliminar esta predicción")

    # Evitar eliminación si el estado es PENDING o RUNNING
    if prediction.status in [PredictionStatus.PENDING, PredictionStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="No se puede eliminar una predicción en estado PENDING o RUNNING")

    # Eliminar los archivos de resultados
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    prediction_file = os.path.join(study_dir, f"{prediction.id}.parquet")
    prediction_tags_file = os.path.join(study_dir, f"{prediction.id}_tags.parquet")

    try:
        if os.path.exists(prediction_file):
            os.remove(prediction_file)
        if os.path.exists(prediction_tags_file):
            os.remove(prediction_tags_file)
    except Exception as e:
        pass

    # Eliminar el trabajo en Redis
    redis_client.delete(prediction.id)

    # Eliminar la predicción
    prediction = crud.prediction.remove(db=db, id=prediction_id)

    return prediction

@router.get("/{prediction_id}/download_results", response_class=StreamingResponse)
def download_prediction_results(
    *,
    db: Session = Depends(deps.get_db),
    prediction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> StreamingResponse:
    """
    Descargar los resultados de una predicción en formato CSV.
    """
    # Verificar que la predicción existe
    prediction = crud.prediction.get(db=db, id=prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    # Verificar permisos
    study = crud.study.get(db=db, id=prediction.study_id)
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a esta predicción")

    # Verificar que la predicción está en estado COMPLETE
    if prediction.status != PredictionStatus.COMPLETE:
        raise HTTPException(status_code=400, detail="La predicción aún no ha sido completada")

    # Definir los posibles nombres de columnas
    spanish_columns = ["eutrofizacion", "químicas", "físicas", "adicionales"]
    english_columns = ["eutrophication", "chemical", "physical", "additional"]

    # Construir las rutas a los archivos
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    prediction_file = os.path.join(study_dir, f"{prediction.id}.parquet")
    prediction_tags_file = os.path.join(study_dir, f"{prediction.id}_tags.parquet")

    # Verificar que los archivos existen
    if not os.path.exists(prediction_file) or not os.path.exists(prediction_tags_file):
        raise HTTPException(status_code=404, detail="Archivos de resultados no encontrados")

    # Cargar los dataframes
    try:
        df_prediction = pd.read_parquet(prediction_file)
        df_prediction_tags = pd.read_parquet(prediction_tags_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al leer los archivos de resultados")

    # Seleccionar las columnas disponibles
    available_columns = [col for col in spanish_columns if col in df_prediction.columns]
    if not available_columns:
        raise HTTPException(status_code=400, detail="No hay columnas disponibles en los resultados")

    # Renombrar las columnas al inglés
    column_mapping = {spanish: english for spanish, english in zip(spanish_columns, english_columns)}
    df_prediction.rename(columns=column_mapping, inplace=True)
    df_prediction_tags.rename(columns=column_mapping, inplace=True)

    # Añadir la columna adicional 'eutrofizacion_inferida' al dataframe de tags
    df_prediction_tags.rename(columns={'eutrofizacion_inferida': 'eutrophication_inferred'}, inplace=True)

    # Crear columnas de tags y agregar 'eutrophication_inferred'
    for col in available_columns:
        english_col = column_mapping[col]
        if english_col in df_prediction_tags.columns:
            df_prediction[english_col + "_tag"] = df_prediction_tags[english_col]
    # Añadir 'eutrophication_inferred' si existe
    if 'eutrophication_inferred' in df_prediction_tags.columns:
        df_prediction['eutrophication_inferred'] = df_prediction_tags['eutrophication_inferred']

    # Unificar las columnas disponibles
    result_columns = []
    for col in available_columns:
        english_col = column_mapping[col]
        result_columns.append(english_col)
        if english_col + "_tag" in df_prediction.columns:
            result_columns.append(english_col + "_tag")
    # Añadir 'eutrophication_inferred' al final si existe
    if 'eutrophication_inferred' in df_prediction.columns:
        result_columns.append('eutrophication_inferred')

    # Seleccionar las columnas finales
    df_result = df_prediction[result_columns]

    # Convertir el dataframe a CSV en memoria
    csv_buffer = StringIO()
    df_result.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Retornar el CSV como respuesta de descarga
    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=prediction_{prediction.id}_results.csv"}
    )


@router.get("/{prediction_id}/results", response_class=JSONResponse)
def get_prediction_results(
    *,
    db: Session = Depends(deps.get_db),
    prediction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener los resultados de una predicción en formato JSON.
    """
    # Verificar que la predicción existe
    prediction = crud.prediction.get(db=db, id=prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Predicción no encontrada")

    # Verificar permisos
    study = crud.study.get(db=db, id=prediction.study_id)
    project = crud.project.get(db=db, id=study.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a esta predicción")

    # Verificar que la predicción está en estado COMPLETE
    if prediction.status != PredictionStatus.COMPLETE:
        raise HTTPException(status_code=400, detail="La predicción aún no ha sido completada")

    # Definir los posibles nombres de columnas
    spanish_columns = ["eutrofizacion", "quimicas", "fisicas", "adicionales"]
    english_columns = ["eutrophication", "chemical", "physical", "additional"]

    # Construir las rutas a los archivos
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    study_dir = os.path.join(project_dir, str(study.id))
    prediction_file = os.path.join(study_dir, f"{prediction.id}.parquet")
    prediction_tags_file = os.path.join(study_dir, f"{prediction.id}_tags.parquet")

    # Verificar que los archivos existen
    if not os.path.exists(prediction_file) or not os.path.exists(prediction_tags_file):
        raise HTTPException(status_code=404, detail="Archivos de resultados no encontrados")

    # Cargar los dataframes
    try:
        df_prediction = pd.read_parquet(prediction_file)
        df_prediction_tags = pd.read_parquet(prediction_tags_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al leer los archivos de resultados")

    # Seleccionar las columnas disponibles
    available_columns = [col for col in spanish_columns if col in df_prediction.columns]
    if not available_columns:
        raise HTTPException(status_code=400, detail="No hay columnas disponibles en los resultados")

    # Renombrar las columnas al inglés
    column_mapping = {spanish: english for spanish, english in zip(spanish_columns, english_columns)}
    df_prediction.rename(columns=column_mapping, inplace=True)
    df_prediction_tags.rename(columns=column_mapping, inplace=True)

    # Añadir la columna adicional 'eutrofizacion_inferida' al dataframe de tags
    df_prediction_tags.rename(columns={'eutrofizacion_inferida': 'eutrophication_inferred'}, inplace=True)

    # Crear columnas de tags y agregar 'eutrophication_inferred'
    for col in available_columns:
        english_col = column_mapping[col]
        if english_col in df_prediction_tags.columns:
            df_prediction[english_col + "_tag"] = df_prediction_tags[english_col]
    # Añadir 'eutrophication_inferred' si existe
    if 'eutrophication_inferred' in df_prediction_tags.columns:
        df_prediction['eutrophication_inferred'] = df_prediction_tags['eutrophication_inferred']

    # Unificar las columnas disponibles
    result_columns = []
    for col in available_columns:
        english_col = column_mapping[col]
        result_columns.append(english_col)
        if english_col + "_tag" in df_prediction.columns:
            result_columns.append(english_col + "_tag")
    # Añadir 'eutrophication_inferred' al final si existe
    if 'eutrophication_inferred' in df_prediction.columns:
        result_columns.append('eutrophication_inferred')

    # Seleccionar las columnas finales
    df_result = df_prediction[result_columns]

    # Convertir el dataframe a JSON
    result_json = df_result.to_dict(orient="records")

    # Retornar el JSON
    return JSONResponse(content=result_json)