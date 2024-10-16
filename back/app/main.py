# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.initial_data import init_variables

app = FastAPI(title=settings.PROJECT_NAME)

origins = [
    "*",  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Inicializar la base de datos
    init_db()

    # Crear una sesión de base de datos
    db = SessionLocal()

    # Cargar las variables iniciales
    init_variables(db)

    # Cerrar la sesión
    db.close()

app.include_router(api_router, prefix=settings.API_V1_STR)
