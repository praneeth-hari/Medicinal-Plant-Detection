"""
Global Exception Handlers
==========================
Centralised error handling for the FastAPI application.
Converts exceptions into consistent JSON error responses.

Exception Hierarchy::

    AppException (base)
    ├── NotFoundException       (404)
    ├── AlreadyExistsException  (409)
    ├── UnauthorizedException   (401)
    ├── ForbiddenException      (403)
    ├── BadRequestException     (400)
    └── ServiceUnavailableException (503)
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# Custom Exception Classes
# ══════════════════════════════════════════════════════════════════

class AppException(Exception):
    """Base application exception.

    All custom business-logic exceptions should inherit from this.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code for the response.
        detail: Optional structured detail payload.
    """

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str = "Resource", resource_id: Any = None) -> None:
        detail_msg = f"{resource} not found"
        if resource_id is not None:
            detail_msg = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=detail_msg,
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "resource": resource,
                "id": str(resource_id) if resource_id else None,
            },
        )


class AlreadyExistsException(AppException):
    """Resource already exists / duplicate (409)."""

    def __init__(self, resource: str = "Resource", field: str = "") -> None:
        detail_msg = f"{resource} already exists"
        if field:
            detail_msg = f"{resource} with this {field} already exists"
        super().__init__(
            message=detail_msg,
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "ALREADY_EXISTS",
                "resource": resource,
                "field": field,
            },
        )


class UnauthorizedException(AppException):
    """Authentication required or failed (401)."""

    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED"},
        )


class ForbiddenException(AppException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN"},
        )


class BadRequestException(AppException):
    """Invalid request data (400)."""

    def __init__(self, message: str = "Bad request", detail: Any = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or {"code": "BAD_REQUEST"},
        )


class ServiceUnavailableException(AppException):
    """External service or component unavailable (503)."""

    def __init__(self, service: str = "Service") -> None:
        super().__init__(
            message=f"{service} is currently unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "SERVICE_UNAVAILABLE", "service": service},
        )


# ══════════════════════════════════════════════════════════════════
# Helper
# ══════════════════════════════════════════════════════════════════

def _error_response(
    status_code: int,
    message: str,
    detail: Any = None,
) -> JSONResponse:
    """Build a consistent JSON error response."""
    body: dict[str, Any] = {
        "success": False,
        "message": message,
    }
    if detail is not None:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


# ══════════════════════════════════════════════════════════════════
# Registration
# ══════════════════════════════════════════════════════════════════

def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app.

    Call this once during application startup, **before** the app
    starts serving requests.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException,
    ) -> JSONResponse:
        logger.warning(
            "AppException: %s [%d] path=%s",
            exc.message,
            exc.status_code,
            request.url.path,
        )
        return _error_response(exc.status_code, exc.message, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError,
    ) -> JSONResponse:
        errors = []
        for err in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(loc) for loc in err.get("loc", [])),
                    "message": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
            )
        logger.warning(
            "Validation error: path=%s errors=%s",
            request.url.path,
            errors,
        )
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation error",
            {"code": "VALIDATION_ERROR", "errors": errors},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError,
    ) -> JSONResponse:
        logger.error(
            "Database integrity error: %s path=%s",
            exc.orig,
            request.url.path,
        )
        message = "A database constraint was violated"
        if "UNIQUE" in str(exc.orig).upper():
            message = "A record with this value already exists"
        return _error_response(
            status.HTTP_409_CONFLICT,
            message,
            {"code": "INTEGRITY_ERROR"},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request, exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.error(
            "Database error: %s path=%s",
            exc,
            request.url.path,
            exc_info=True,
        )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "A database error occurred",
            {"code": "DATABASE_ERROR"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception: %s path=%s",
            exc,
            request.url.path,
            exc_info=True,
        )
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An internal server error occurred",
            {"code": "INTERNAL_ERROR"},
        )
