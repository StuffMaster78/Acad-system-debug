from __future__ import annotations

from typing import Any

from rest_framework.exceptions import PermissionDenied


def get_request_website(request: Any):
    website = getattr(request, "website", None)

    if website is None:
        raise PermissionDenied("Tenant could not be resolved.")

    return website


def get_request_portal(request: Any):
    return getattr(request, "portal", None)