"""Pydantic request/response schemas for the Guest Book API."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class ChildCreate(BaseModel):
    """Schema for creating an accompanying child."""

    name: str = Field(max_length=255)
    position: int = Field(ge=1, le=4)


class ChildResponse(BaseModel):
    """Schema for child in API responses."""

    id: uuid.UUID
    name: str
    position: int

    model_config = {"from_attributes": True}


class GuestCreate(BaseModel):
    """Schema for creating a new guest record."""

    stay_from: date
    stay_to: date
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    date_of_birth: date
    birth_place: str = Field(max_length=500)
    nationality: str = Field(max_length=255)
    permanent_address: str
    travel_purpose: str = Field(max_length=500)
    passport_number: str = Field(max_length=100)
    visa_details: str | None = None
    children: list[ChildCreate] = Field(default_factory=list, max_length=4)

    @field_validator("stay_to")
    @classmethod
    def stay_to_after_stay_from(cls, v: date, info: object) -> date:
        """Validate that stay_to is not before stay_from."""
        stay_from = info.data.get("stay_from")  # type: ignore[union-attr]
        if stay_from and v < stay_from:
            raise ValueError("stay_to must be >= stay_from")
        return v


class GuestResponse(BaseModel):
    """Schema for a guest record in API responses."""

    id: uuid.UUID
    stay_from: date
    stay_to: date
    first_name: str
    last_name: str
    date_of_birth: date
    birth_place: str
    nationality: str
    permanent_address: str
    travel_purpose: str
    passport_number: str
    visa_details: str | None
    accommodation_name: str
    accommodation_address: str
    children: list[ChildResponse]
    pdf_generated_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GuestListResponse(BaseModel):
    """Paginated list of guest records."""

    items: list[GuestResponse]
    total: int
    page: int
    size: int


class ConfigResponse(BaseModel):
    """Read-only accommodation configuration for frontend pre-fill."""

    accommodation_name: str
    accommodation_address: str
