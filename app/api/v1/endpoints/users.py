from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.crud import user as user_crud
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Регистрация нового пользователя.
    """
    # Проверяем, существует ли уже пользователь с таким email
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован",
        )

    # Проверяем, существует ли уже пользователь с таким username
    user = user_crud.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем пользователя уже зарегистрирован",
        )

    # Создаем пользователя
    user = user_crud.create(db, user_create=user_in)
    return user


@router.get("/me", response_model=UserPublic)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Получение информации о текущем пользователе.
    """
    return current_user


@router.put("/me", response_model=UserPublic)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновление информации о текущем пользователе.
    """
    # Проверка на уникальность email, если он изменяется
    if user_in.email and user_in.email != current_user.email:
        user = user_crud.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует",
            )

    # Проверка на уникальность username, если он изменяется
    if user_in.username and user_in.username != current_user.username:
        user = user_crud.get_by_username(db, username=user_in.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем пользователя уже существует",
            )

    # Обновляем пользователя
    user = user_crud.update(db, db_user=current_user, user_update=user_in)
    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Получение информации о пользователе по ID.
    """
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Удаление пользователя (только для администраторов).
    """
    user = user_crud.get_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    # Запрещаем удалять администраторам самих себя
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно удалить себя",
        )

    user_crud.delete(db, db_user=user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
