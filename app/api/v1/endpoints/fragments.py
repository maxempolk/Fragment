from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.crud import fragment as fragment_crud
# from app.models.fragment import Fragment
from app.models.user import User
from app.schemas.fragment import (
    FragmentCreate,
    FragmentListResponse,
    FragmentResponse,
    FragmentUpdate,
)
from app.schemas.tag import TagResponse
from app.schemas.user import UserPublic

router = APIRouter()


@router.post("/", response_model=FragmentResponse, status_code=status.HTTP_201_CREATED)
def create_fragment(
    *,
    db: Session = Depends(get_db),
    fragment_in: FragmentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Создание нового фрагмента кода.
    """
    fragment = fragment_crud.create(db, fragment_create=fragment_in, author_id=current_user.id)

    # Получаем фрагмент с дополнительной информацией для ответа
    fragment_with_info = fragment_crud.get_by_id(
        db, fragment_id=fragment.id, current_user_id=current_user.id
    )

    if not fragment_with_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    return prepare_fragment_response(db, fragment_with_info, current_user.id)


@router.get("/", response_model=FragmentListResponse)
def read_fragments(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    author_id: Optional[int] = None,
    language: Optional[str] = None,
    tag: Optional[str] = None,
    liked_by_user: Optional[int] = None,
    search: Optional[str] = None,
    include_private: bool = False,
    current_user: Optional[User] = Depends(get_current_active_user),
) -> Any:
    """
    Получение списка фрагментов кода с возможностью фильтрации.
    """
    # Получаем IP-адрес для анонимных пользователей
    # client_host = request.client.host if request.client else None

    # Для администраторов показываем все фрагменты, включая приватные
    admin_view = current_user and bool(current_user.is_admin) and include_private

    # Получаем ID текущего пользователя (если есть)
    current_user_id = current_user.id if current_user else None

    fragments, total = fragment_crud.get_multi(
        db=db,
        skip=skip,
        limit=limit,
        current_user_id=current_user_id,
        filter_author_id=author_id,
        filter_language=language,
        filter_tag=tag,
        filter_liked_by_user=liked_by_user,
        search_query=search,
        include_private=admin_view,
    )

    # Подготавливаем ответ
    fragment_responses = [
        prepare_fragment_response(db, fragment_data, current_user_id)
        for fragment_data in fragments
    ]

    return {
        "items": fragment_responses,
        "total": total
    }


@router.get("/{fragment_id}", response_model=FragmentResponse)
def read_fragment(
    *,
    request: Request,
    fragment_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user),
) -> Any:
    """
    Получение фрагмента кода по ID.
    """
    # Получаем IP-адрес для учета просмотров
    client_host = request.client.host if request.client else None

    # Получаем ID текущего пользователя (если есть)
    current_user_id = current_user.id if current_user else None

    fragment_data = fragment_crud.get_by_id(
        db, fragment_id=fragment_id, current_user_id=current_user_id
    )

    if not fragment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    # Проверяем доступ: либо фрагмент публичный, либо пользователь - автор или админ
    fragment = fragment_data["fragment"]
    if not fragment.is_public and (
        not current_user or
        (fragment.author_id != current_user.id and not bool(current_user.is_admin))
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому фрагменту"
        )

    # Учитываем просмотр
    fragment_crud.add_view(
        db,
        fragment_id=fragment_id,
        user_id=current_user_id,
        ip_address=client_host
    )

    return prepare_fragment_response(db, fragment_data, current_user_id)


@router.put("/{fragment_id}", response_model=FragmentResponse)
def update_fragment(
    *,
    fragment_id: int,
    fragment_in: FragmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Обновление фрагмента кода.
    """
    fragment_data = fragment_crud.get_by_id(
        db, fragment_id=fragment_id, current_user_id=current_user.id
    )

    if not fragment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    fragment = fragment_data["fragment"]

    # Проверяем права: только автор или администратор могут редактировать фрагмент
    if fragment.author_id != current_user.id and not bool(current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления этого фрагмента"
        )

    # Обновляем фрагмент
    updated_fragment = fragment_crud.update(
        db, db_fragment=fragment, fragment_update=fragment_in
    )

    # Получаем обновленный фрагмент с дополнительной информацией
    fragment_data = fragment_crud.get_by_id(
        db, fragment_id=updated_fragment.id, current_user_id=current_user.id
    )

    if not fragment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    return prepare_fragment_response(db, fragment_data, current_user.id)


@router.delete("/{fragment_id}")
def delete_fragment(
    *,
    fragment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Удаление фрагмента кода.
    """
    fragment_data = fragment_crud.get_by_id(
        db, fragment_id=fragment_id, current_user_id=current_user.id
    )

    if not fragment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фрагмент не найден"
        )

    fragment = fragment_data["fragment"]

    # Проверяем права: только автор или администратор могут удалить фрагмент
    if fragment.author_id != current_user.id and not bool(current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления этого фрагмента"
        )

    # Удаляем фрагмент
    fragment_crud.delete(db, db_fragment=fragment)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Вспомогательная функция для подготовки ответа
def prepare_fragment_response(db: Session, fragment_data: dict[str, Any], current_user_id: Optional[int]) -> FragmentResponse:
    """Подготовка полного ответа с информацией о фрагменте"""
    fragment = fragment_data["fragment"]

    # Явно создаем объект UserPublic из модели User
    author_data = UserPublic(
        id=fragment.author.id,
        username=fragment.author.username,
        bio=fragment.author.bio,
        created_at=fragment.author.created_at
    )

    # Явно создаем список объектов TagResponse из моделей Tag
    tags_data: List[TagResponse] = []
    for tag in fragment.tags:
        tag_response = TagResponse(
            id=tag.id,
            name=tag.name,
            created_at=tag.created_at
        )
        tags_data.append(tag_response)

    # Создаем объект FragmentResponse
    return FragmentResponse(
        id=fragment.id,
        title=fragment.title,
        content=fragment.content,
        language=fragment.language,
        description=fragment.description,
        is_public=fragment.is_public,
        author_id=fragment.author_id,
        created_at=fragment.created_at,
        updated_at=fragment.updated_at,
        likes_count=fragment_data["likes_count"],
        views_count=fragment_data["views_count"],
        is_liked_by_current_user=fragment_data["is_liked_by_current_user"] if current_user_id else None,
        author=author_data,
        tags=tags_data
    )
