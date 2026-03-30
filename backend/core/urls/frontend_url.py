from __future__ import annotations

from urllib.parse import urljoin

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