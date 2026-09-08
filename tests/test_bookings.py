import os
from datetime import date, timedelta

import aiohttp
import pytest

APP_URL = os.getenv("APP_URL", "http://localhost:8000")


@pytest.fixture
async def client() -> aiohttp.ClientSession:
    async with aiohttp.ClientSession(base_url=APP_URL) as session:
        yield session


def booking_payload(*, days_from_today: int, booking_time: str) -> dict[str, object]:
    return {
        "name": "Анна Петрова",
        "phone": "+79991234567",
        "booking_date": (date.today() + timedelta(days=days_from_today)).isoformat(),
        "booking_time": booking_time,
        "guests": 4,
    }


async def create_booking(
    client: aiohttp.ClientSession, payload: dict[str, object]
) -> dict[str, object]:
    async with client.post("/bookings", json=payload) as response:
        assert response.status == 201, await response.text()
        return await response.json()


async def test_creates_gets_filters_and_cancels_booking(client: aiohttp.ClientSession) -> None:
    payload = booking_payload(days_from_today=1, booking_time="12:00")
    created = await create_booking(client, payload)
    assert created["status"] == "active"
    assert created["id"] > 0

    async with client.get(f"/bookings/{created['id']}") as response:
        assert response.status == 200
        assert await response.json() == created

    async with client.get("/bookings", params={"date": payload["booking_date"]}) as response:
        assert response.status == 200
        assert created in await response.json()

    async with client.delete(f"/bookings/{created['id']}") as response:
        assert response.status == 200
        cancelled = await response.json()
        assert cancelled["status"] == "cancelled"

    async with client.get(f"/bookings/{created['id']}") as response:
        assert response.status == 200
        assert (await response.json())["status"] == "cancelled"

    replacement = await create_booking(client, payload)
    assert replacement["id"] != created["id"]
    assert replacement["status"] == "active"


async def test_rejects_duplicate_active_booking(client: aiohttp.ClientSession) -> None:
    payload = booking_payload(days_from_today=2, booking_time="13:00")
    await create_booking(client, payload)

    async with client.post("/bookings", json=payload) as response:
        assert response.status == 409
        assert await response.json() == {"detail": "Booking slot is already taken"}


@pytest.mark.parametrize(
    "payload",
    [
        {**booking_payload(days_from_today=3, booking_time="14:30")},
        {**booking_payload(days_from_today=-1, booking_time="15:00")},
        {**booking_payload(days_from_today=91, booking_time="16:00")},
        {**booking_payload(days_from_today=4, booking_time="17:00"), "name": "A"},
        {**booking_payload(days_from_today=5, booking_time="18:00"), "phone": "+7123"},
        {**booking_payload(days_from_today=6, booking_time="19:00"), "guests": 13},
    ],
)
async def test_rejects_invalid_booking_payload(
    client: aiohttp.ClientSession, payload: dict[str, object]
) -> None:
    async with client.post("/bookings", json=payload) as response:
        assert response.status == 422


async def test_returns_not_found_for_unknown_booking(client: aiohttp.ClientSession) -> None:
    async with client.get("/bookings/999999") as response:
        assert response.status == 404
        assert await response.json() == {"detail": "Время занято"}

    async with client.delete("/bookings/999999") as response:
        assert response.status == 404
        assert await response.json() == {"detail": "Запись не найдена"}
