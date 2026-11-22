import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

STATUS_CODES: dict[int, str] = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHENTICATED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
}


def _envelope(status: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"code": STATUS_CODES.get(status, "INTERNAL_ERROR"), "message": message},
    )


async def _http_exception_handler(_: Request, exc: Exception) -> Response:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    detail = exc.detail if isinstance(exc.detail, str) else "request failed"
    return _envelope(exc.status_code, detail)


async def _validation_exception_handler(_: Request, exc: Exception) -> Response:
    if not isinstance(exc, RequestValidationError):
        raise exc
    return _envelope(422, "request validation failed")


async def _unhandled_exception_handler(_: Request, exc: Exception) -> Response:
    logger.error("unhandled exception", exc_info=exc)
    return _envelope(500, "internal server error")


def register_error_handlers(app: FastAPI) -> None:
    """对外错误一律 { code, message }；业务代码只抛 HTTPException。"""
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
