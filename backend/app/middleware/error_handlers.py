from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    NotAuthorisedError,
    PasswordTooShortError,
    RewindError,
    SideFullError,
    SpotifyNotConfiguredError,
    SpotifyUnavailableError,
    TapeNotFoundError,
    TapeNotInDraftError,
    TrackNotFoundError,
)

# Maps each exception class to (http_status_code, error_code_string)
ERROR_MAP = {
    EmailAlreadyRegisteredError: (409, "Conflict"),
    InvalidCredentialsError: (401, "Unauthorized"),
    PasswordTooShortError: (422, "ValidationError"),
    TapeNotFoundError: (404, "NotFound"),
    TrackNotFoundError: (404, "NotFound"),
    NotAuthorisedError: (403, "Forbidden"),
    TapeNotInDraftError: (409, "Conflict"),
    SideFullError: (422, "ValidationError"),
    SpotifyNotConfiguredError: (503, "ServiceUnavailable"),
    SpotifyUnavailableError: (502, "BadGateway"),
}


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(RewindError)
    async def rewind_error_handler(request: Request, exc: RewindError) -> JSONResponse:
        status_code, error_code = ERROR_MAP.get(type(exc), (500, "InternalServerError"))
        logger.warning(
            "Domain error: {} {} - {}",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "error": error_code,
                "message": exc.message,
                "details": {},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: {} {}", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": {},
            },
        )
