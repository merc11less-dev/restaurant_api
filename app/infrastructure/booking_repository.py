from datetime import date, time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.booking import Booking, BookingDraft, BookingStatus
from app.domain.errors import BookingAlreadyExistsError
from app.infrastructure.models import BookingModel


class SqlAlchemyBookingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_active_slot_taken(self, booking_date: date, booking_time: time) -> bool:
        statement = select(BookingModel.id).where(
            BookingModel.booking_date == booking_date,
            BookingModel.booking_time == booking_time,
            BookingModel.status == BookingStatus.ACTIVE.value,
        )
        return (await self._session.scalar(statement)) is not None

    async def add(self, draft: BookingDraft) -> Booking:
        model = BookingModel(
            name=draft.name,
            phone=draft.phone,
            booking_date=draft.booking_date,
            booking_time=draft.booking_time,
            guests=draft.guests,
            status=BookingStatus.ACTIVE.value,
        )
        self._session.add(model)
        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            if self._is_unique_violation(error):
                raise BookingAlreadyExistsError from error
            raise
        await self._session.refresh(model)
        return self._to_domain(model)

    async def list(self, booking_date: date | None) -> list[Booking]:
        statement = select(BookingModel).order_by(
            BookingModel.booking_date, BookingModel.booking_time
        )
        if booking_date is not None:
            statement = statement.where(BookingModel.booking_date == booking_date)
        models = (await self._session.scalars(statement)).all()
        return [self._to_domain(model) for model in models]

    async def get(self, booking_id: int) -> Booking | None:
        model = await self._session.get(BookingModel, booking_id)
        return self._to_domain(model) if model is not None else None

    async def cancel(self, booking_id: int) -> Booking | None:
        model = await self._session.get(BookingModel, booking_id)
        if model is None:
            return None
        model.status = BookingStatus.CANCELLED.value
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: BookingModel) -> Booking:
        return Booking(
            id=model.id,
            name=model.name,
            phone=model.phone,
            booking_date=model.booking_date,
            booking_time=model.booking_time,
            guests=model.guests,
            status=BookingStatus(model.status),
            created_at=model.created_at,
        )

    @staticmethod
    def _is_unique_violation(error: IntegrityError) -> bool:
        return getattr(error.orig, "sqlstate", None) == "23505" or getattr(
            error.orig, "sqlite_errorcode", None
        ) in {1555, 2067}
