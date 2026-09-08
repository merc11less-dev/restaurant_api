from datetime import date, time

from app.domain.booking import Booking, BookingDraft
from app.domain.errors import BookingAlreadyExistsError, BookingNotFoundError
from app.domain.repositories import BookingRepository


class BookingService:
    def __init__(self, repository: BookingRepository) -> None:
        self._repository = repository

    async def create(
        self,
        *,
        name: str,
        phone: str,
        booking_date: date,
        booking_time: time,
        guests: int,
    ) -> Booking:
        if await self._repository.is_active_slot_taken(booking_date, booking_time):
            raise BookingAlreadyExistsError

        return await self._repository.add(
            BookingDraft(
                name=name,
                phone=phone,
                booking_date=booking_date,
                booking_time=booking_time,
                guests=guests,
            )
        )

    async def list(self, booking_date: date | None) -> list[Booking]:
        return await self._repository.list(booking_date)

    async def get(self, booking_id: int) -> Booking:
        booking = await self._repository.get(booking_id)
        if booking is None:
            raise BookingNotFoundError
        return booking

    async def cancel(self, booking_id: int) -> Booking:
        booking = await self._repository.cancel(booking_id)
        if booking is None:
            raise BookingNotFoundError
        return booking
