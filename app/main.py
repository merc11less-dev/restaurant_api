from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.routes.bookings import router as bookings_router

app = FastAPI(
    title="Restaurant Booking API",
)

app.include_router(bookings_router)

register_exception_handlers(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}