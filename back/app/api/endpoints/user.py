import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app import models, schemas, crud
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate
):
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    user = crud.user.create(db=db, user_in=user_in)

    # Crear directorio de usuario
    user_data_dir = os.path.join(settings.USER_DATA, user.id)
    os.makedirs(user_data_dir, exist_ok=True)

    return user

@router.post("/login", response_model=schemas.Token)
def login_access_token(
    *,
    db: Session = Depends(deps.get_db),
    login_data: schemas.UserLogin
):
    user = crud.user.get_by_email(db, email=login_data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user)
):
    return current_user

@router.post("/change-password")
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    password_change: schemas.PasswordChange,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    # Verificar que la contraseña antigua es correcta
    if not security.verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    # Actualizar a la nueva contraseña
    hashed_password = security.get_password_hash(password_change.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    return {"msg": "Password updated successfully"}
