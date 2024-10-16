# app/api/endpoints/dataset.py

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.api import deps
import os
import io
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

@router.get("/{dataset_id}/data", response_model=schemas.DatasetPage)
def read_dataset_page(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    page_size: int = Query(100, gt=0),
    page_number: int = Query(1, gt=0),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Obtener una página de datos del dataset.
    """
    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este dataset")

    # Ruta del archivo Parquet
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")

    # Cargar los datos
    try:
        df = pd.read_parquet(dataset_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Water Body", "Sample Date"] + [var.id for var in dataset.variables])

    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size  # Calcular el número total de páginas

    if page_number > total_pages and total_rows > 0:
        return {
            "data": [],
            "page_size": page_size,
            "page_number": page_number+1,
            "total_rows": total_rows,
            "total_pages": page_number,
        }

    # Obtener el rango de filas para la página solicitada
    start = (page_number - 1) * page_size
    end = start + page_size

    data = df.iloc[start:end].fillna("").to_dict(orient="records")

    return {
        "data": data,
        "page_size": page_size,
        "page_number": page_number,
        "total_rows": total_rows,
        "total_pages": total_pages,
    }

@router.put("/{dataset_id}/data", response_model=schemas.DatasetPage)
def update_dataset_page(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    data_in: schemas.DatasetPageUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Actualizar una página de datos del dataset.
    """
    page_size = data_in.page_size
    page_number = data_in.page_number
    new_data = data_in.data

    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para modificar este dataset")

    # Ruta del archivo Parquet
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")

    # Cargar los datos existentes
    try:
        df = pd.read_parquet(dataset_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Water Body", "Sample Date"] + [var.id for var in dataset.variables])

    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size if total_rows > 0 else 1

    start = (page_number - 1) * page_size
    end = start + page_size

    # Validar que los datos no excedan el tamaño de página
    if len(new_data) > page_size:
        raise HTTPException(status_code=400, detail="Cantidad de datos excede el tamaño de página")

    # Convertir los datos entrantes a DataFrame
    df_new = pd.DataFrame(new_data)

    # Reemplazar filas existentes o agregar nuevas
    if start >= total_rows:
        # Agregar al final
        df = pd.concat([df, df_new], ignore_index=True)
    else:
        # Actualizar filas existentes
        # Asegurar que el DataFrame tiene suficientes filas
        if end > total_rows:
            # Extender el DataFrame con filas vacías si es necesario
            empty_rows = pd.DataFrame(index=range(total_rows, end), columns=df.columns)
            df = pd.concat([df, empty_rows], ignore_index=True)

        # Actualizar las filas correspondientes
        for i, row in enumerate(new_data):
            idx = start + i
            if idx >= len(df):
                break  # Por seguridad, aunque debería estar cubierto
            if all(value in [None, ""] for value in row.values()):
                # Eliminar fila si todos los campos son nulos
                df.drop(idx, inplace=True)
            else:
                df.iloc[idx] = row

        # Eliminar filas vacías sin tener en cuenta las dos primeras columnas
        df.dropna(subset=df.columns[2:], how="all", inplace=True)

        # Resetear índices después de eliminar filas
        df.reset_index(drop=True, inplace=True)

    # Actualizar el número de filas
    dataset.rows = len(df)
    db.add(dataset)
    db.commit()

    # Guardar el DataFrame actualizado
    df.to_parquet(dataset_file, index=False)

    # Retornar la información de la página actualizada
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size if total_rows > 0 else 1

    data = df.iloc[start:end].fillna("").to_dict(orient="records")

    return {
        "data": data,
        "page_size": page_size,
        "page_number": page_number,
        "total_rows": total_rows,
        "total_pages": total_pages,
    }

@router.post("/{dataset_id}/upload_csv")
def upload_dataset_csv(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Subir un archivo CSV para reemplazar los datos del dataset.
    """
    # Obtener el dataset y verificar permisos
    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para modificar este dataset")

    # Leer el archivo CSV en un DataFrame de pandas
    try:
        df_uploaded = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer el archivo CSV: {str(e)}")

    # Verificar que la columna "Sample Date" exista
    if "Sample Date" not in df_uploaded.columns:
        raise HTTPException(status_code=400, detail='El archivo CSV debe contener la columna "Sample Date"')

    # Obtener las variables del dataset
    variables = dataset.variables  # Suponiendo que devuelve una lista de objetos variable con 'name' y 'id'
    variable_names = [var.id for var in variables]
    variable_name_to_id = {var.name: var.id for var in variables}

    # Columnas a conservar
    columns_to_keep = ["Sample Date"] + variable_names

    # Seleccionar solo las columnas necesarias
    df_selected = df_uploaded[columns_to_keep]

    # Renombrar las columnas de variables para usar los IDs
    df_selected = df_selected.rename(columns=variable_name_to_id)

    # Reindexar el DataFrame para asegurarnos de que todas las columnas de variables estén presentes
    columns_order = ["Sample Date"] + [var.id for var in variables]
    df_selected = df_selected.reindex(columns=columns_order)

    # Agregar la columna "Water Body" con el nombre del proyecto
    df_selected["Water Body"] = project.name

    # Definir el orden final de las columnas
    final_columns_order = ["Water Body", "Sample Date"] + [var.id for var in variables]
    df_selected = df_selected[final_columns_order]

    # Eliminar filas vacías sin tener en cuenta las dos primeras columnas
    df_selected.dropna(subset=df_selected.columns[2:], how="all", inplace=True)

    # Resetear índices después de eliminar filas
    df_selected.reset_index(drop=True, inplace=True)

    # Guardar el DataFrame en formato Parquet, reemplazando el archivo existente
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")

    df_selected.to_parquet(dataset_file, index=False)

    # Actualizar el número de filas en el dataset
    dataset.rows = len(df_selected)
    db.add(dataset)
    db.commit()

    return {"detail": "Dataset actualizado exitosamente"}

@router.get("/{dataset_id}/download_csv")
def download_dataset_csv(
    *,
    db: Session = Depends(deps.get_db),
    dataset_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Descargar el dataset en formato CSV.
    """
    # Obtener el dataset y verificar permisos
    dataset = crud.dataset.get(db=db, id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset no encontrado")

    project = crud.project.get(db=db, id=dataset.project_id)
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para acceder a este dataset")

    # Ruta del archivo Parquet
    user_data_dir = os.path.join(settings.USER_DATA, str(current_user.id))
    project_dir = os.path.join(user_data_dir, str(project.id))
    dataset_file = os.path.join(project_dir, f"{dataset.id}.parquet")

    # Cargar los datos
    try:
        df = pd.read_parquet(dataset_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Archivo de datos no encontrado")

    # Eliminar la columna "Water Body"
    if "Water Body" in df.columns:
        df = df.drop(columns=["Water Body"])

    # Convertir el DataFrame a CSV en memoria
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    fix_name = dataset.name.replace(" ", "_").lower()

    # Crear la respuesta StreamingResponse
    response = StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
    )
    response.headers["Content-Disposition"] = f"attachment; filename={fix_name}.csv"
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"

    return response
