"""Guest CRUD routes mounted at /api/guests."""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import current_active_user
from app.database import get_session
from app.main import get_app_config
from app.models import Child, Guest, User
from app.schemas import GuestCreate, GuestListResponse, GuestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/guests", tags=["guests"])


@router.post("", response_model=GuestResponse, status_code=201)
async def create_guest(
    data: GuestCreate,
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(current_active_user),
) -> Guest:
    """Create a new guest record with accommodation snapshotted from config."""
    config = get_app_config()

    guest = Guest(
        stay_from=data.stay_from,
        stay_to=data.stay_to,
        first_name=data.first_name,
        last_name=data.last_name,
        date_of_birth=data.date_of_birth,
        birth_place=data.birth_place,
        nationality=data.nationality,
        permanent_address=data.permanent_address,
        travel_purpose=data.travel_purpose,
        passport_number=data.passport_number,
        visa_details=data.visa_details,
        accommodation_name=config.accommodation.name,
        accommodation_address=config.accommodation.address,
    )
    for child_data in data.children:
        guest.children.append(
            Child(name=child_data.name, position=child_data.position)
        )

    session.add(guest)
    await session.commit()
    await session.refresh(guest, ["children"])
    return guest


@router.get("", response_model=GuestListResponse)
async def list_guests(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    nationality: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(current_active_user),
) -> dict:
    """List guests with pagination and optional filters."""
    from datetime import date as date_type

    query = select(Guest).options(selectinload(Guest.children))
    count_query = select(func.count(Guest.id))

    if search:
        pattern = f"%{search}%"
        query = query.where(
            Guest.first_name.ilike(pattern) | Guest.last_name.ilike(pattern)
        )
        count_query = count_query.where(
            Guest.first_name.ilike(pattern) | Guest.last_name.ilike(pattern)
        )

    if nationality:
        query = query.where(Guest.nationality == nationality)
        count_query = count_query.where(Guest.nationality == nationality)

    if date_from:
        d = date_type.fromisoformat(date_from)
        query = query.where(Guest.stay_from >= d)
        count_query = count_query.where(Guest.stay_from >= d)

    if date_to:
        d = date_type.fromisoformat(date_to)
        query = query.where(Guest.stay_from <= d)
        count_query = count_query.where(Guest.stay_from <= d)

    query = query.order_by(Guest.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    guests = result.scalars().unique().all()

    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    return {"items": guests, "total": total, "page": page, "size": size}


@router.get("/{guest_id}", response_model=GuestResponse)
async def get_guest(
    guest_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(current_active_user),
) -> Guest:
    """Get a single guest by ID."""
    query = (
        select(Guest)
        .options(selectinload(Guest.children))
        .where(Guest.id == guest_id)
    )
    result = await session.execute(query)
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


@router.delete("/{guest_id}", status_code=204)
async def delete_guest(
    guest_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(current_active_user),
) -> None:
    """Delete a guest and cascade-delete children."""
    query = select(Guest).where(Guest.id == guest_id)
    result = await session.execute(query)
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    await session.delete(guest)
    await session.commit()


@router.post("/{guest_id}/pdf")
async def generate_guest_pdf(
    guest_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _user: User = Depends(current_active_user),
) -> dict:
    """Generate a PDF for the guest and upload it to Google Drive."""
    from app.services.drive import upload_to_drive
    from app.services.pdf import generate_pdf

    query = (
        select(Guest)
        .options(selectinload(Guest.children))
        .where(Guest.id == guest_id)
    )
    result = await session.execute(query)
    guest = result.scalar_one_or_none()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    try:
        pdf_buffer = generate_pdf(guest)
    except Exception as e:
        logger.error("PDF generation failed for guest %s: %s", guest_id, e)
        raise HTTPException(status_code=500, detail="PDF generation failed")

    filename = f"{guest.last_name}_{guest.first_name}_{guest.stay_from}.pdf"
    config = get_app_config()

    try:
        url = upload_to_drive(pdf_buffer, filename, config.google_drive.folder_id)
    except Exception as e:
        logger.error("Drive upload failed for guest %s: %s", guest_id, e)
        raise HTTPException(status_code=500, detail="Google Drive upload failed")

    guest.pdf_generated_at = datetime.now(timezone.utc)
    await session.commit()

    return {"url": url, "filename": filename}
