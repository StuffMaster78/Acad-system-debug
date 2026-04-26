from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response


def not_found_response(message: str = "Resource not found.") -> Response:
    """
    Return a stable 404 API response.
    """

    return Response(
        {"detail": message},
        status=status.HTTP_404_NOT_FOUND,
    )


def bad_request_response(message: str) -> Response:
    """
    Return a stable 400 API response.
    """

    return Response(
        {"detail": message},
        status=status.HTTP_400_BAD_REQUEST,
    )