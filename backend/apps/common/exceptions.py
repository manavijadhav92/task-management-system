"""
Centralized exception handling.

DRF's default exception handler is wrapped so that EVERY error response
(auth errors, permission errors, validation errors, not-found, throttling,
and unexpected 500s) comes back in the same {"success": false, ...} shape,
and so that unexpected exceptions never leak internal details (stack
traces, database errors, etc.) to the client.
"""

import logging

from rest_framework.views import exception_handler as drf_exception_handler

from .responses import error_response

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Raised by view/service code for a controlled, user-facing error."""

    def __init__(self, message, errors=None, status=400):
        self.message = message
        self.errors = errors or {}
        self.status = status
        super().__init__(message)


def custom_exception_handler(exc, context):
    if isinstance(exc, ApiError):
        return error_response(exc.message, exc.errors, exc.status)

    response = drf_exception_handler(exc, context)

    if response is not None:
        detail = response.data
        message = "Request failed"
        errors = detail

        if isinstance(detail, dict) and "detail" in detail and len(detail) == 1:
            message = str(detail["detail"])
            errors = {}
        elif isinstance(detail, dict):
            message = "Validation failed"

        return error_response(message, errors, response.status_code)

    # Unexpected/unhandled exception -> log full detail server-side,
    # return a safe generic message to the client.
    logger.exception("Unhandled exception", exc_info=exc)
    return error_response(
        "An unexpected error occurred. Please try again later.",
        {},
        500,
    )
