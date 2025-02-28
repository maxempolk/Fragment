# tests/test_crud/test_tag.py
from sqlalchemy.orm.session import Session

from datetime import datetime
from app.crud.tag import (
    get_by_id, get_by_name, get_multi, create, get_or_create,
    get_or_create_tags, delete
)
from app.schemas.tag import TagCreate
from app.models.tag import Tag

def test_get_by_id(db_session: Session):
    """Тест получения тега по ID"""
    # Создаем тестовый тег
    test_tag = Tag(name="test-tag")
    db_session.add(test_tag)
    db_session.commit()
    db_session.refresh(test_tag)

    # Вызов тестируемой функции
    retrieved_tag = get_by_id(db_session, tag_id=test_tag.id)

    # Проверка результата
    assert retrieved_tag is not None
    assert retrieved_tag.id == test_tag.id
    assert retrieved_tag.name == test_tag.name

    # Тест с несуществующим ID
    assert get_by_id(db_session, tag_id=9999) is None

def test_get_by_name(db_session: Session):
    """Тест получения тега по имени"""
    # Создаем тестовый тег
    test_tag = Tag(name="test-tag-name")
    db_session.add(test_tag)
    db_session.commit()
    db_session.refresh(test_tag)

    # Вызов тестируемой функции
    retrieved_tag = get_by_name(db_session, name=test_tag.name)

    # Проверка результата
    assert retrieved_tag is not None
    assert retrieved_tag.id == test_tag.id
    assert retrieved_tag.name == test_tag.name

    # Тест с несуществующим именем
    assert get_by_name(db_session, name="nonexistent-tag") is None

def test_get_multi(db_session: Session):
    """Тест получения списка тегов"""
    # Создаем тестовые теги
    test_tags = [
        Tag(name="tag1"),
        Tag(name="tag2"),
        Tag(name="tag3"),
        Tag(name="othertag"),
    ]
    for tag in test_tags:
        db_session.add(tag)
    db_session.commit()

    # Вызов тестируемой функции без поиска
    tags, total = get_multi(db_session)

    # Проверка результата
    assert total == 4
    assert len(tags) == 4

    # Вызов тестируемой функции с поиском
    tags, total = get_multi(db_session, search="tag")

    # Проверка результата
    assert total == 4  # "tag" содержится во всех тегах

    # Вызов тестируемой функции с более конкретным поиском
    tags, total = get_multi(db_session, search="other")

    # Проверка результата
    assert total == 1
    assert tags[0].name == "othertag"

    # Вызов тестируемой функции с пагинацией
    tags, total = get_multi(db_session, skip=1, limit=2)

    # Проверка результата
    assert total == 4  # Всего 4 тега
    assert len(tags) == 2  # Но получаем только 2

def test_create(db_session: Session):
    """Тест создания нового тега"""
    # Подготовка тестовых данных
    tag_create = TagCreate(name="newtag")

    # Вызов тестируемой функции
    created_tag = create(db_session, tag_create=tag_create)

    # Проверка результата
    assert created_tag.id is not None
    assert created_tag.name == tag_create.name
    assert isinstance(created_tag.created_at, datetime)

def test_get_or_create(db_session: Session):
    """Тест получения существующего тега или создания нового"""
    # Создаем тестовый тег
    test_tag = Tag(name="existing-tag")
    db_session.add(test_tag)
    db_session.commit()
    db_session.refresh(test_tag)

    # Вызов тестируемой функции для существующего тега
    retrieved_tag = get_or_create(db_session, name=test_tag.name)

    # Проверка результата
    assert retrieved_tag.id == test_tag.id

    # Вызов тестируемой функции для нового тега
    new_tag = get_or_create(db_session, name="new-unique-tag")

    # Проверка результата
    assert new_tag.id is not None
    assert new_tag.name == "new-unique-tag"

def test_get_or_create_tags(db_session: Session):
    """Тест получения или создания списка тегов"""
    # Создаем тестовый тег
    test_tag = Tag(name="existing-tag")
    db_session.add(test_tag)
    db_session.commit()
    db_session.refresh(test_tag)

    # Подготовка тестовых данных
    tag_names = ["existing-tag", "new-tag1", "new-tag2", "", " "]

    # Вызов тестируемой функции
    tags = get_or_create_tags(db_session, tag_names=tag_names)

    # Проверка результата
    assert len(tags) == 3  # Пустые строки должны быть отфильтрованы
    assert any(tag.name == "existing-tag" for tag in tags)
    assert any(tag.name == "new-tag1" for tag in tags)
    assert any(tag.name == "new-tag2" for tag in tags)

def test_delete(db_session: Session):
    """Тест удаления тега"""
    # Создаем тестовый тег
    test_tag = Tag(name="tag-to-delete")
    db_session.add(test_tag)
    db_session.commit()
    db_session.refresh(test_tag)

    # Вызов тестируемой функции
    result = delete(db_session, db_tag=test_tag)

    # Проверка результата
    assert result is True
    assert get_by_id(db_session, tag_id=test_tag.id) is None
