from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.core.database import get_db
from app.crud import tag as tag_crud
from app.models.user import User
from app.schemas.tag import TagCreate, TagListResponse, TagResponse

router = APIRouter()

@router.get("/", response_model=TagListResponse)
def read_tags(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> Any:
    """
    Получение списка тегов с возможностью поиска.
    """
    tags, total = tag_crud.get_multi(
        db=db, skip=skip, limit=limit, search=search
    )

    return {
        "items": tags,
        "total": total
    }


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    *,
    db: Session = Depends(get_db),
    tag_in: TagCreate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Создание нового тега (только для администраторов).
    """
    # Проверяем, существует ли уже тег с таким названием
    existing_tag = tag_crud.get_by_name(db, name=tag_in.name)
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Тег с таким названием уже существует"
        )

    tag = tag_crud.create(db, tag_create=tag_in)
    return tag


@router.delete("/{tag_id}")
def delete_tag(
    *,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    Удаление тега (только для администраторов).
    """
    tag = tag_crud.get_by_id(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тег не найден"
        )

    tag_crud.delete(db, db_tag=tag)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
