from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud import fragment as fragment_crud, like as like_crud
from app.models.user import User

router = APIRouter()


@router.post("/{fragment_id}")
def like_fragment(
    *,
    fragment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Поставить лайк фрагменту кода.
    """
    # Проверяем, существует ли фрагмент
    fragment_data = fragment_crud.get_by_id(
        db, fragment_id=fragment_id, current_user_id=current_user.id
    )

    if not fragment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    fragment = fragment_data["fragment"]

    # Проверяем доступ: нельзя лайкать приватные фрагменты других пользователей
    if not fragment.is_public and fragment.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому фрагменту"
        )

    # Проверяем, лайкнул ли пользователь уже этот фрагмент
    if fragment_data["is_liked_by_current_user"]:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # Добавляем лайк
    like_crud.create(db, fragment_id=fragment_id, user_id=current_user.id)

    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/{fragment_id}")
def unlike_fragment(
    *,
    fragment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удалить лайк с фрагмента кода.
    """
    # Проверяем, существует ли фрагмент
    fragment_data = fragment_crud.get_by_id(
        db, fragment_id=fragment_id, current_user_id=current_user.id
    )

    if not fragment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    # Проверяем, лайкнул ли пользователь этот фрагмент
    if not fragment_data["is_liked_by_current_user"]:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # Удаляем лайк
    like = like_crud.get_by_fragment_and_user(
        db, fragment_id=fragment_id, user_id=current_user.id
    )

    if like:
        like_crud.delete(db, db_like=like)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
