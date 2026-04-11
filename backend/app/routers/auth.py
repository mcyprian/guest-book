"""Authentication routes (login) mounted at /api/auth."""

from fastapi import APIRouter

from app.auth import auth_backend, fastapi_users
from app.schemas_auth import UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])

router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
