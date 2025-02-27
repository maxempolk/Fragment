from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.models.fragment import Fragment
from app.models.tag import Tag, fragment_tag_association
from app.models.like import Like
from app.models.view import View
# from app.models.user import User
from app.schemas.fragment import FragmentCreate, FragmentUpdate
from app.crud.tag import get_or_create_tags


def get_by_id(
    db: Session,
    fragment_id: int,
    current_user_id: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """Получение фрагмента по ID с дополнительной информацией"""
    query = (
        db.query(
            Fragment,
            func.count(Like.id).label("likes_count"),
            func.count(View.id).label("views_count"),
            func.count(Like.id).filter(Like.user_id == current_user_id).label("user_liked")
        )
        .outerjoin(Like, Like.fragment_id == Fragment.id)
        .outerjoin(View, View.fragment_id == Fragment.id)
        .filter(Fragment.id == fragment_id)
        .group_by(Fragment.id)
    )

    result = query.first()

    if not result:
        return None

    fragment, likes_count, views_count, user_liked = result

    # Проверка доступа: либо фрагмент публичный, либо текущий пользователь - автор
    if not fragment.is_public and (current_user_id is None or fragment.author_id != current_user_id):
        return None

    return {
        "fragment": fragment,
        "likes_count": likes_count,
        "views_count": views_count,
        "is_liked_by_current_user": bool(user_liked)
    }


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    current_user_id: Optional[int] = None,
    filter_author_id: Optional[int] = None,
    filter_language: Optional[str] = None,
    filter_tag: Optional[str] = None,
    filter_liked_by_user: Optional[int] = None,
    search_query: Optional[str] = None,
    include_private: bool = False
) -> Tuple[List[Dict[str, Any]], int]:
    """Получение списка фрагментов с пагинацией и фильтрацией"""
    # Базовый запрос
    query = (
        db.query(
            Fragment,
            func.count(Like.id).label("likes_count"),
            func.count(View.id).label("views_count"),
            func.count(Like.id).filter(Like.user_id == current_user_id).label("user_liked")
        )
        .outerjoin(Like, Like.fragment_id == Fragment.id)
        .outerjoin(View, View.fragment_id == Fragment.id)
    )

    # Учитываем приватные фрагменты
    if not include_private:
        # Показываем только публичные фрагменты + приватные фрагменты текущего пользователя
        if current_user_id:
            query = query.filter(
                or_(
                    Fragment.is_public == True,
                    and_(Fragment.is_public == False, Fragment.author_id == current_user_id)
                )
            )
        else:
            query = query.filter(Fragment.is_public == True)
    else:
        # Для администратора: показываем все фрагменты
        pass

    # Применяем дополнительные фильтры
    if filter_author_id:
        query = query.filter(Fragment.author_id == filter_author_id)

    if filter_language:
        query = query.filter(Fragment.language == filter_language)

    if filter_tag:
        query = query.join(
            fragment_tag_association,
            fragment_tag_association.c.fragment_id == Fragment.id
        ).join(
            Tag,
            and_(
                Tag.id == fragment_tag_association.c.tag_id,
                Tag.name == filter_tag
            )
        )

    if filter_liked_by_user:
        query = query.join(
            Like,
            and_(
                Like.fragment_id == Fragment.id,
                Like.user_id == filter_liked_by_user
            )
        )

    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                Fragment.title.ilike(search),
                Fragment.description.ilike(search),
                Fragment.content.ilike(search)
            )
        )

    # Получаем общее количество результатов
    total = query.group_by(Fragment.id).count()

    # Применяем пагинацию и получаем результаты
    results = query.group_by(Fragment.id).order_by(Fragment.created_at.desc()).offset(skip).limit(limit).all()

    fragments: List[Dict[str, Any]] = []
    for fragment, likes_count, views_count, user_liked in results:
        fragments.append({
            "fragment": fragment,
            "likes_count": likes_count,
            "views_count": views_count,
            "is_liked_by_current_user": bool(user_liked)
        })

    return fragments, total


def create(
    db: Session,
    fragment_create: FragmentCreate,
    author_id: int
) -> Fragment:
    """Создание нового фрагмента"""
    # Создаем новый фрагмент
    db_fragment = Fragment(
        title=fragment_create.title,
        content=fragment_create.content,
        language=fragment_create.language,
        description=fragment_create.description,
        is_public=fragment_create.is_public,
        author_id=author_id
    )
    db.add(db_fragment)
    db.flush()

    # Добавляем теги, если они указаны
    if fragment_create.tags:
        tags = get_or_create_tags(db, fragment_create.tags)
        db_fragment.tags = tags

    db.commit()
    db.refresh(db_fragment)
    return db_fragment


def update(
    db: Session,
    db_fragment: Fragment,
    fragment_update: FragmentUpdate
) -> Fragment:
    """Обновление фрагмента"""
    update_data = fragment_update.model_dump(exclude_unset=True)

    # Обрабатываем теги отдельно
    tags = None
    if "tags" in update_data:
        tags = update_data.pop("tags")

    # Обновляем остальные поля
    for key, value in update_data.items():
        setattr(db_fragment, key, value)

    # Обновляем теги, если они были указаны
    if tags is not None:
        new_tags = get_or_create_tags(db, tags)
        db_fragment.tags = new_tags

    db.add(db_fragment)
    db.commit()
    db.refresh(db_fragment)
    return db_fragment


def delete(db: Session, db_fragment: Fragment) -> bool:
    """Удаление фрагмента"""
    db.delete(db_fragment)
    db.commit()
    return True


def add_view(
    db: Session,
    fragment_id: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> View:
    """Добавление просмотра фрагмента"""
    view = View(
        fragment_id=fragment_id,
        user_id=user_id,
        ip_address=ip_address
    )
    db.add(view)
    db.commit()
    db.refresh(view)
    return view
