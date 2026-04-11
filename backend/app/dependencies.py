"""Shared FastAPI dependencies."""

from fastapi import Depends

from app.auth import current_active_user
from app.config import AppConfig
from app.main import get_app_config
from app.models import User


def get_config(
    _user: User = Depends(current_active_user),
) -> AppConfig:
    """Return app config, requiring authentication."""
    return get_app_config()
