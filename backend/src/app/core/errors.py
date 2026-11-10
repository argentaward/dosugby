"""Доменные ошибки.

Сервисы кидают только эти исключения и ничего не знают об HTTP.
Перевод в HTTP-ответ происходит в одном месте — в обработчике ниже.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"


class ValidationError(DomainError):
    code = "validation_error"


_STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def _status_for(exc: DomainError) -> int:
    for error_type, code in _STATUS_BY_ERROR.items():
        if isinstance(exc, error_type):
            return code
    return status.HTTP_400_BAD_REQUEST


async def _domain_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, DomainError):  # pragma: no cover - защита от неверной регистрации
        raise exc
    return JSONResponse(
        status_code=_status_for(exc),
        content={"error": {"code": exc.code, "message": exc.message}},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error_handler)
