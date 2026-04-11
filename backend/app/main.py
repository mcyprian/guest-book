"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_user_manager, get_user_db
from app.config import Settings, load_config, AppConfig
from app.database import create_tables, get_session

logger = logging.getLogger(__name__)

app_config: AppConfig | None = None


def get_app_config() -> AppConfig:
    """Return the loaded application config."""
    if app_config is None:
        raise RuntimeError("App config not loaded")
    return app_config


async def seed_first_user(settings: Settings) -> None:
    """Create the first user from environment variables if it doesn't exist."""
    from fastapi_users.exceptions import UserAlreadyExists
    from app.schemas_auth import UserCreate

    async for session in get_session():
        async for user_db in get_user_db(session):
            async for user_manager in get_user_manager(user_db):
                try:
                    await user_manager.create(
                        UserCreate(
                            email=settings.first_user_email,
                            password=settings.first_user_password,
                        )
                    )
                    logger.info("Seeded first user: %s", settings.first_user_email)
                except UserAlreadyExists:
                    logger.debug("First user already exists, skipping seed.")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: load config, create tables, seed user."""
    global app_config
    from app.config import settings

    app_config = load_config()
    logger.info("Loaded config for: %s", app_config.accommodation.name)

    await create_tables()
    await seed_first_user(settings)

    yield


app = FastAPI(title="Guest Book", version="1.0.0", lifespan=lifespan)

# CORS
from app.config import settings as _settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.routers.auth import router as auth_router
from app.routers.guests import router as guests_router
from app.routers.config import router as config_router

app.include_router(auth_router)
app.include_router(guests_router)
app.include_router(config_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
