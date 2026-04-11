"""User schemas for fastapi-users authentication."""

import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data."""


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
