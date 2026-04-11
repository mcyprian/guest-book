"""Configuration endpoint mounted at /api/config."""

from fastapi import APIRouter, Depends

from app.config import AppConfig
from app.dependencies import get_config
from app.schemas import ConfigResponse

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=ConfigResponse)
async def get_accommodation_config(
    config: AppConfig = Depends(get_config),
) -> dict:
    """Return accommodation name and address for frontend pre-fill."""
    return {
        "accommodation_name": config.accommodation.name,
        "accommodation_address": config.accommodation.address,
    }
