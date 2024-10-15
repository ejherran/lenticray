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
    output_tag = prediction.name.lower().replace(" ", "_")
    job_data = {
        'id': prediction.id,
        'payload': {
            'id': prediction.id,
            'work_dir': study_dir,
            'window_size': prediction.window_size,
            'amount': prediction.amount,
            'output_tag': output_tag,
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

    # Eliminar el trabajo en Redis
    redis_client.delete(prediction.id)

    # Eliminar la predicción
    prediction = crud.prediction.remove(db=db, id=prediction_id)

    return prediction
