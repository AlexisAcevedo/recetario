"""
Router principal de API v1.
Agrupa todos los routers de la versión 1.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.me import router as me_router
from app.api.v1.roles import router as roles_router

router = APIRouter()

# Incluir todos los routers con sus prefijos
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(me_router, prefix="/me", tags=["me"])
router.include_router(roles_router, prefix="/roles", tags=["roles"])

