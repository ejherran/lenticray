from fastapi import APIRouter
from app.api.endpoints import user, project, dataset, variable, study, prediction

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(project.router, prefix="/projects", tags=["projects"])
api_router.include_router(dataset.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(variable.router, prefix="/variables", tags=["variables"])
api_router.include_router(study.router, prefix="/studies", tags=["studies"])
api_router.include_router(prediction.router, prefix="/predictions", tags=["predictions"])