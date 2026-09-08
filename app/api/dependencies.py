from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.booking_service import BookingService
from app.infrastructure.booking_repository import SqlAlchemyBookingRepository
from app.infrastructure.database import get_session


def get_booking_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BookingService:
    return BookingService(SqlAlchemyBookingRepository(session))
