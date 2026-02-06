"""
API v1 Router - Aggregates all v1 routers.
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.me import router as me_router

router = APIRouter()

# Include all routers with their prefixes
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(me_router, prefix="/me", tags=["me"])
