from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors import BookingAlreadyExistsError, BookingNotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BookingNotFoundError)
    async def handle_not_found(_: Request, __: BookingNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": "Запись не найдена"})

    @app.exception_handler(BookingAlreadyExistsError)
    async def handle_conflict(_: Request, __: BookingAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": "Время занято"})
