"""SQLAlchemy ORM models for Guest Book."""

import uuid
from datetime import date, datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Date, DateTime, ForeignKey, Index, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model managed by fastapi-users."""

    __tablename__ = "users"


class Guest(Base):
    """Foreign guest stay record."""

    __tablename__ = "guests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    stay_from: Mapped[date] = mapped_column(Date, nullable=False)
    stay_to: Mapped[date] = mapped_column(Date, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    birth_place: Mapped[str] = mapped_column(String(500), nullable=False)
    nationality: Mapped[str] = mapped_column(String(255), nullable=False)
    permanent_address: Mapped[str] = mapped_column(Text, nullable=False)
    travel_purpose: Mapped[str] = mapped_column(String(500), nullable=False)
    passport_number: Mapped[str] = mapped_column(String(100), nullable=False)
    visa_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    accommodation_name: Mapped[str] = mapped_column(String(500), nullable=False)
    accommodation_address: Mapped[str] = mapped_column(String(500), nullable=False)
    pdf_generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    children: Mapped[list["Child"]] = relationship(
        back_populates="guest", cascade="all, delete-orphan", order_by="Child.position"
    )


class Child(Base):
    """Accompanying child of a guest."""

    __tablename__ = "children"
    __table_args__ = (Index("ix_children_guest_id", "guest_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    guest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guests.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    guest: Mapped["Guest"] = relationship(back_populates="children")
