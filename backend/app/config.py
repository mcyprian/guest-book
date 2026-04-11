"""Application configuration loaded from config.yaml and environment variables."""

from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AccommodationConfig(BaseModel):
    """Accommodation provider details (from config.yaml)."""

    name: str
    address: str


class GoogleDriveConfig(BaseModel):
    """Google Drive upload settings (from config.yaml)."""

    folder_id: str


class AppConfig(BaseModel):
    """Application configuration loaded from config.yaml."""

    accommodation: AccommodationConfig
    google_drive: GoogleDriveConfig


class Settings(BaseSettings):
    """Environment-based settings (secrets and runtime config)."""

    database_url: str = "postgresql+asyncpg://guestbook:guestbook@db:5432/guestbook"
    jwt_secret: str = "change-me-in-production"
    jwt_lifetime_seconds: int = 3600
    first_user_email: str = "admin@example.com"
    first_user_password: str = "changeme"
    google_service_account_key_path: str = "/app/credentials/service-account.json"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Load application config from a YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    return AppConfig(**data)


settings = Settings()
