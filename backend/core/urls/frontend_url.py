"""
Frontend URL builder utilities.

Provide a centralized way to construct frontend URLs with
query parameters in a consistent and safe manner.
"""
from __future__ import annotations
from urllib.parse import urlencode, urljoin
from typing import Optional, Dict, Any

from django.conf import settings

from users.models.user import User


def _normalize_base_url(base_url: str) -> str:
    """
    Normalize a base URL so downstream joins are predictable.
    """
    return base_url.rstrip("/") + "/"


def get_frontend_base_url_for_user(user: User) -> str:
    """
    Return the frontend base URL for a user.

    Tenant website domain is preferred. Falls back to the global frontend URL.
    """
    website = getattr(user, "website", None)

    if website is not None and getattr(website, "domain", None):
        return _normalize_base_url(website.domain)

    fallback = getattr(
        settings,
        "FRONTEND_BASE_URL",
        "https://app.example.com",
    )
    return _normalize_base_url(fallback)


def build_frontend_url_for_user(user: User, path: str) -> str:
    """
    Build a tenant-aware frontend URL for a user.
    """
    base_url = get_frontend_base_url_for_user(user)
    normalized_path = path.lstrip("/")
    return urljoin(base_url, normalized_path)


def get_profile_url(user: User) -> str:
    """
    Return the profile page URL for a user.
    """
    return build_frontend_url_for_user(user, "/profile/")


def get_settings_url(user: User) -> str:
    """
    Return the settings page URL for a user.
    """
    return build_frontend_url_for_user(user, "/settings/")


def get_security_settings_url(user: User) -> str:
    """
    Return the security settings page URL for a user.
    """
    return build_frontend_url_for_user(user, "/settings/security/")


def get_login_url(user: User | None = None) -> str:
    """
    Return the login page URL.

    If a user is provided and has a tenant domain, prefer that domain.
    Otherwise use the global frontend base URL.
    """
    if user is not None:
        return build_frontend_url_for_user(user, "/login/")

    fallback = getattr(
        settings,
        "FRONTEND_BASE_URL",
        "https://app.example.com",
    )
    return urljoin(_normalize_base_url(fallback), "login/")


def get_profile_edit_url(user: User) -> str:
    """
    Return the profile edit page URL for a user.
    """
    return build_frontend_url_for_user(user, "/profile/edit/")


def get_frontend_base_url(website=None) -> str:
    """
    Resolve the base frontend URL.

    Args:
        website: Optional website/tenant instance.

    Returns:
        The base frontend URL.
    """
    # If you later support per-tenant domains:
    if website and hasattr(website, "domain") and website.domain:
        return website.domain.rstrip("/")

    return getattr(settings, "FRONTEND_URL", "").rstrip("/")



def get_frontend_link(
    *,
    path: str,
    query_params: dict | None = None,
    website=None,
) -> str:
    """
    Build a full frontend URL.

    Args:
        path: Frontend route (e.g. "/auth/magic-link")
        query_params: Optional query parameters
        website: Optional tenant context

    Returns:
        Fully qualified frontend URL.
    """
    base_url = get_frontend_base_url(website=website)

    path = path if path.startswith("/") else f"/{path}"

    url = f"{base_url}{path}"

    if query_params:
        query_string = urlencode(query_params)
        url = f"{url}?{query_string}"

    return url


def build_frontend_url(
    *,
    path: str,
    query_params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> str:
    """
    Build a frontend URL with optional query parameters.

    Args:
        path: Frontend route path (e.g., "/verify-email-change").
        query_params: Optional dictionary of query parameters.
        base_url: Optional override for frontend base URL.

    Returns:
        Fully constructed frontend URL.
    """
    base = (base_url or settings.FRONTEND_URL).rstrip("/")

    # Ensure path starts with "/"
    if not path.startswith("/"):
        path = f"/{path}"

    url = urljoin(base + "/", path.lstrip("/"))

    if query_params:
        # Remove None values to avoid messy URLs
        clean_params = {
            key: value
            for key, value in query_params.items()
            if value is not None
        }
        if clean_params:
            return f"{url}?{urlencode(clean_params)}"

    return url