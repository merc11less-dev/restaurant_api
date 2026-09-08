import re
from datetime import date, time, timedelta

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.booking import BookingStatus

PHONE_PATTERN = re.compile(r"(?:\+7|8)\d{10}$")
NAME_PATTERN = re.compile(r"[^\W\d_]+(?:[ -][^\W\d_]+)*$", re.UNICODE)
FIRST_BOOKING_HOUR = 12
LAST_BOOKING_HOUR = 22


class BookingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120, examples=["Анна Петрова"])
    phone: str = Field(examples=["+79991234567"])
    booking_date: date = Field(examples=["2026-08-20"])
    booking_time: time = Field(examples=["19:00"])
    guests: int = Field(ge=1, le=12, examples=[4])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 2:
            raise ValueError("Имя должно содержать минимум два символа")
        if not NAME_PATTERN.fullmatch(normalized):
            raise ValueError("Имя может содержать только буквы, пробелы и дефисы")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Телефон должен соответствовать формату +7XXXXXXXXXX или 8XXXXXXXXXX")
        return value

    @field_validator("booking_date")
    @classmethod
    def validate_booking_date(cls, value: date) -> date:
        today = date.today()
        if value < today or value > today + timedelta(days=90):
            raise ValueError("Дата записи должна быть от сегодняшнего дня до следующих 90 дней")
        return value

    @field_validator("booking_time")
    @classmethod
    def validate_booking_time(cls, value: time) -> time:
        if (
            value.hour < FIRST_BOOKING_HOUR
            or value.hour > LAST_BOOKING_HOUR
            or value.minute != 0
            or value.second != 0
            or value.microsecond != 0
        ):
            raise ValueError("Время записи должно быть указано с шагом в 1 час, с 12:00 до 22:00")
        return value


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    booking_date: date
    booking_time: time
    guests: int
    status: BookingStatus
