# tests/test_crud/test_fragment.py
from sqlalchemy.orm.session import Session

from app.crud.fragment import (
    get_by_id, get_multi, create, update, delete, add_view
)
from app.schemas.fragment import FragmentCreate, FragmentUpdate
from app.models.fragment import Fragment
from app.models.user import User
from app.models.tag import Tag
from app.models.like import Like
from app.models.view import View

def test_get_by_id(db_session: Session, normal_user: User):
    """Тест получения фрагмента по ID"""
    # Создаем тестовый фрагмент
    test_fragment = Fragment(
        title="Test Fragment",
        content="print('Hello, World!')",
        language="python",
        description="Test description",
        is_public=True,
        author_id=normal_user.id
    )
    db_session.add(test_fragment)
    db_session.commit()
    db_session.refresh(test_fragment)

    # Вызов тестируемой функции без текущего пользователя
    fragment_data = get_by_id(db_session, fragment_id=test_fragment.id)

    # Проверка результата
    assert fragment_data is not None
    assert fragment_data["fragment"].id == test_fragment.id
    assert fragment_data["likes_count"] == 0
    assert fragment_data["views_count"] == 0
    assert fragment_data["is_liked_by_current_user"] is False

    # Добавляем лайк и просмотр
    like = Like(fragment_id=test_fragment.id, user_id=normal_user.id)
    view = View(fragment_id=test_fragment.id, user_id=normal_user.id)
    db_session.add(like)
    db_session.add(view)
    db_session.commit()

    # Вызов тестируемой функции с текущим пользователем
    fragment_data = get_by_id(db_session, fragment_id=test_fragment.id, current_user_id=normal_user.id)

    # Проверка результата
    assert fragment_data["likes_count"] == 1
    assert fragment_data["views_count"] == 1
    assert fragment_data["is_liked_by_current_user"] is True

    # Проверка приватного фрагмента
    private_fragment = Fragment(
        title="Private Fragment",
        content="Secret code",
        language="python",
        description="Private description",
        is_public=False,
        author_id=normal_user.id
    )
    db_session.add(private_fragment)
    db_session.commit()
    db_session.refresh(private_fragment)

    # Доступ владельца к приватному фрагменту
    fragment_data = get_by_id(db_session, fragment_id=private_fragment.id, current_user_id=normal_user.id)
    assert fragment_data is not None

    # Доступ другого пользователя к приватному фрагменту
    another_user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password="hashed_pass",
        is_active=True
    )
    db_session.add(another_user)
    db_session.commit()
    db_session.refresh(another_user)

    fragment_data = get_by_id(db_session, fragment_id=private_fragment.id, current_user_id=another_user.id)
    assert fragment_data is None  # Не должен быть доступен

def test_get_multi(db_session: Session, normal_user: User, admin_user: User):
    """Тест получения списка фрагментов"""
    # Создаем тестовые фрагменты
    fragments = [
        Fragment(
            title="Public Fragment 1",
            content="print('Hello 1')",
            language="python",
            description="Public 1",
            is_public=True,
            author_id=normal_user.id
        ),
        Fragment(
            title="Public Fragment 2",
            content="console.log('Hello 2')",
            language="javascript",
            description="Public 2",
            is_public=True,
            author_id=normal_user.id
        ),
        Fragment(
            title="Private Fragment",
            content="print('Secret')",
            language="python",
            description="Private",
            is_public=False,
            author_id=normal_user.id
        ),
        Fragment(
            title="Admin Fragment",
            content="print('Admin')",
            language="python",
            description="Admin's",
            is_public=True,
            author_id=admin_user.id
        )
    ]
    for fragment in fragments:
        db_session.add(fragment)
    db_session.commit()

    # Создаем теги и добавляем их к фрагментам
    python_tag = Tag(name="python")
    js_tag = Tag(name="javascript")
    db_session.add(python_tag)
    db_session.add(js_tag)
    db_session.commit()
    db_session.refresh(python_tag)
    db_session.refresh(js_tag)

    fragments[0].tags.append(python_tag)
    fragments[1].tags.append(js_tag)
    db_session.commit()

    # Вызов тестируемой функции без фильтров - анонимный пользователь
    fragments_list, total = get_multi(db_session)

    # Проверка результата - должны видеть только публичные фрагменты
    assert total == 3  # 3 публичных фрагмента

    # Вызов тестируемой функции - текущий пользователь
    fragments_list, total = get_multi(db_session, current_user_id=normal_user.id)

    # Проверка результата - должны видеть свои фрагменты (включая приватные)
    assert total == 4

    # Фильтр по автору
    fragments_list, total = get_multi(
        db_session, filter_author_id=admin_user.id, current_user_id=normal_user.id
    )
    assert total == 1

    # Фильтр по языку
    fragments_list, total = get_multi(
        db_session, filter_language="python", current_user_id=normal_user.id
    )
    assert total == 3

    # Фильтр по тегу
    fragments_list, total = get_multi(
        db_session, filter_tag="javascript", current_user_id=normal_user.id
    )
    assert total == 1

    # Поиск
    fragments_list, total = get_multi(
        db_session, search_query="Secret", current_user_id=normal_user.id
    )
    assert total == 1

    # Проверка приватности для администратора
    fragments_list, total = get_multi(
        db_session, current_user_id=admin_user.id, include_private=True
    )
    assert total == 4  # Администратор видит все фрагменты

def test_create(db_session: Session, normal_user: User):
    """Тест создания фрагмента"""
    # Создаем тестовые теги
    db_session.add(Tag(name="python"))
    db_session.add(Tag(name="snippet"))
    db_session.commit()

    # Подготовка тестовых данных
    fragment_create = FragmentCreate(
        title="New Fragment",
        content="def test_function():\n    return 'Hello'",
        language="python",
        description="Test fragment description",
        is_public=True,
        tags=["python", "snippet", "new-tag"]
    )

    # Вызов тестируемой функции
    created_fragment = create(db_session, fragment_create=fragment_create, author_id=normal_user.id)

    # Проверка результата
    assert created_fragment.id is not None
    assert created_fragment.title == fragment_create.title
    assert created_fragment.content == fragment_create.content
    assert created_fragment.language == fragment_create.language
    assert created_fragment.description == fragment_create.description
