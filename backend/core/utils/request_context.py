from __future__ import annotations

from typing import Any

from rest_framework.exceptions import PermissionDenied


def get_request_website(request: Any):
    website = getattr(request, "website", None)

    if website is None:
        raise PermissionDenied("Tenant could not be resolved.")

    return website


def resolve_request_website(request: Any):
    """
    Resolve tenant website without raising.

    Priority: request.website (middleware-set from Host header)
    then request.user.website (tenant-scoped user).

    Returns None for platform-level users (superadmin with no website)
    which callers should treat as "no website filter" rather than an error.
    """
    return (
        getattr(request, "website", None)
        or getattr(getattr(request, "user", None), "website", None)
    )


def get_request_portal(request: Any):
    return getattr(request, "portal", None)