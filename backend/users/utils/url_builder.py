from __future__ import annotations

from users.models.user import User


def build_profile_url(user: User) -> str:
    """
    Build the frontend profile URL for a user.
    """
    if user.website and user.website.domain:
        base = user.website.domain.rstrip("/")
    else:
        base = "https://app.example.com"  # fallback

    return f"{base}/profile"