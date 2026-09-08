"""
Consistent JSON response helpers used across every API endpoint.

Every successful response looks like:
    {"success": true, "message": "...", "data": {...}}

Every error response looks like:
    {"success": false, "message": "...", "errors": {...}}
"""

from rest_framework.response import Response


def success_response(message="Success", data=None, status=200, extra=None):
    body = {"success": True, "message": message, "data": data}
    if extra:
        body.update(extra)
    return Response(body, status=status)


def error_response(message="Error", errors=None, status=400):
    return Response(
        {"success": False, "message": message, "errors": errors or {}},
        status=status,
    )
