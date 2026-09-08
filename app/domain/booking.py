from dataclasses import dataclass
from datetime import date, datetime, time
from enum import StrEnum


class BookingStatus(StrEnum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class BookingDraft:
    name: str
    phone: str
    booking_date: date
    booking_time: time
    guests: int


@dataclass(frozen=True, slots=True)
class Booking:
    id: int
    name: str
    phone: str
    booking_date: date
    booking_time: time
    guests: int
    status: BookingStatus
    created_at: datetime
