"""
writer_management/utils.py

Shared utility functions for writer_management.

PROFILE RESOLUTION
------------------
The identity chain is:
    auth.User → accounts.AccountProfile → writer_management.WriterProfile

WriterProfile has no direct link to User.
All resolution must go through AccountProfile.

Use these helpers everywhere — never inline the two-hop.

USAGE
-----
    from writer_management.utils import get_writer_profile, require_writer_profile

    # Returns None if not found — use in views / checks
    profile = get_writer_profile(request.user)
    if profile is None:
        ...

    # Raises WriterProfileNotFoundError — use in services
    profile = require_writer_profile(request.user)
"""

from __future__ import annotations

import logging
from writer_management.models.writer_profile import WriterProfile
from users.models.user import User
from websites.models.websites import Website

logger = logging.getLogger(__name__)


def get_writer_profile(user) -> "WriterProfile | None":
    """
    Resolve WriterProfile from a User instance.

    Resolution chain: User → AccountProfile → WriterProfile

    Returns None if any hop is missing. Never raises.
    Safe to call in views, serializers, and permission classes
    where a missing profile is a normal condition.

    Args:
        user: auth.User instance or any object with account_profiles.

    Returns:
        WriterProfile instance or None.
    """
    from writer_management.models.writer_profile import WriterProfile

    try:
        # User → AccountProfile (ForeignKey, one per website)
        # AccountProfile → WriterProfile (OneToOneField)
        # We use the reverse accessor on AccountProfile
        account_profile = (
            user.account_profiles
            .select_related("writer_profile")
            .filter(writer_profile__isnull=False)
            .first()
        )
        if account_profile is None:
            return None
        return account_profile.writer_profile
    except Exception:
        return None


def get_writer_profile_for_website(user, website) -> "WriterProfile | None":
    """
    Resolve WriterProfile for a specific User + Website combination.

    A user can have AccountProfiles on multiple websites, each with
    a different WriterProfile. This resolves the correct one.

    Returns None if not found. Never raises.

    Args:
        user: auth.User instance.
        website: Website instance.

    Returns:
        WriterProfile instance or None.
    """
    try:
        account_profile = (
            user.account_profiles
            .select_related("writer_profile")
            .get(website=website)
        )
        return getattr(account_profile, "writer_profile", None)
    except Exception:
        return None


def require_writer_profile(user) -> "WriterProfile":
    """
    Resolve WriterProfile from a User instance.

    Like get_writer_profile() but raises WriterProfileNotFoundError
    if the profile does not exist.

    Use inside services where a missing profile is a programming
    error or invalid state — not a normal condition.

    Args:
        user: auth.User instance.

    Returns:
        WriterProfile instance.

    Raises:
        WriterProfileNotFoundError: If no WriterProfile found.
    """
    from writer_management.exceptions import WriterProfileNotFoundError

    profile = get_writer_profile(user)
    if profile is None:
        raise WriterProfileNotFoundError(
            f"No WriterProfile found for User pk="
            f"{getattr(user, 'pk', '?')}. "
            "Ensure AccountProfile and WriterProfile exist for this user."
        )
    return profile


def require_writer_profile_for_website(user, website) -> "WriterProfile":
    """
    Resolve WriterProfile for a specific User + Website.
    Raises WriterProfileNotFoundError if not found.
    """
    from writer_management.exceptions import WriterProfileNotFoundError

    profile = get_writer_profile_for_website(user, website)
    if profile is None:
        raise WriterProfileNotFoundError(
            f"No WriterProfile found for User pk={getattr(user, 'pk', '?')} "
            f"on website pk={getattr(website, 'pk', '?')}."
        )
    return profile


def resolve_website_for_writer(writer_profile) -> "Website | None":
    """
    Resolve the Website for a WriterProfile.

    Resolution order:
        1. writer_profile.writer_level.website (most reliable)
        2. writer_profile.account_profile.website

    Returns None if neither resolves. Never raises.

    Used by services that need the website but do not have it
    passed in directly.
    """
    # Option 1: through writer_level
    level = getattr(writer_profile, "writer_level", None)
    if level is not None:
        website = getattr(level, "website", None)
        if website is not None:
            return website

    # Option 2: through account_profile
    try:
        return writer_profile.account_profile.website
    except Exception:
        pass

    logger.warning(
        "resolve_website_for_writer: cannot resolve website "
        "for writer=%s",
        getattr(writer_profile, "registration_id", "?"),
    )
    return None


def resolve_user_for_writer(writer_profile) -> "User | None":
    """
    Resolve the auth User from a WriterProfile.

    Chain: WriterProfile → AccountProfile → User

    Returns None if not resolvable. Never raises.

    Used by notification services that need the User instance
    to call NotificationService.notify().
    """
    try:
        return writer_profile.account_profile.user
    except Exception:
        logger.warning(
            "resolve_user_for_writer: cannot resolve user "
            "for writer=%s",
            getattr(writer_profile, "registration_id", "?"),
        )
        return None