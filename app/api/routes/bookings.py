from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_booking_service
from app.api.schemas import BookingCreate, BookingRead
from app.application.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])
Service = Annotated[BookingService, Depends(get_booking_service)]
BOOKING_DATE_QUERY = Query(default=None, alias="date")


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(payload: BookingCreate, service: Service) -> BookingRead:
    booking = await service.create(**payload.model_dump())
    return BookingRead.model_validate(booking)


@router.get("", response_model=list[BookingRead])
async def list_bookings(
    service: Service, booking_date: date | None = BOOKING_DATE_QUERY
) -> list[BookingRead]:
    bookings = await service.list(booking_date)
    return [BookingRead.model_validate(booking) for booking in bookings]


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(booking_id: int, service: Service) -> BookingRead:
    return BookingRead.model_validate(await service.get(booking_id))


@router.delete("/{booking_id}", response_model=BookingRead)
async def cancel_booking(booking_id: int, service: Service) -> BookingRead:
    return BookingRead.model_validate(await service.cancel(booking_id))
