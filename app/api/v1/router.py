from fastapi import APIRouter

from app.api.v1.endpoints import users, auth #, fragments, likes, tags

router = APIRouter()

# Подключение маршрутизаторов для различных ресурсов
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(users.router, prefix="/users", tags=["users"])
# router.include_router(fragments.router, prefix="/fragments", tags=["fragments"])
# router.include_router(likes.router, prefix="/likes", tags=["likes"])
# router.include_router(tags.router, prefix="/tags", tags=["tags"])
