from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Integer,
    SmallInteger,
    String,
    Time,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BookingModel(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("guests BETWEEN 1 AND 12", name="ck_bookings_guests_range"),
        CheckConstraint("status IN ('active', 'cancelled')", name="ck_bookings_status"),
        Index(
            "uq_active_booking_slot",
            "booking_date",
            "booking_time",
            unique=True,
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(12))
    booking_date: Mapped[date] = mapped_column(Date)
    booking_time: Mapped[time] = mapped_column(Time)
    guests: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
