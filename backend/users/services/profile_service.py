from __future__ import annotations

from typing import Any

from django.db import transaction

from users.models.profile import UserProfile
from users.models.user import User


class ProfileService:
    """
    Service for working with approved live user profiles.
    """

    @staticmethod
    @transaction.atomic
    def get_or_create_profile(user: User) -> UserProfile:
        """
        Return the user's profile, creating it if it does not exist.
        """
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    @transaction.atomic
    def update_profile_fields(
        profile: UserProfile,
        **changes: Any,
    ) -> UserProfile:
        """
        Update approved profile fields directly.

        Use this only for trusted internal operations.
        Do not use this for client or writer self-service edits that require
        review first.
        """
        allowed_fields = {
            "display_name",
            "bio",
            "avatar",
            "timezone",
            "locale",
            "country",
            "last_seen_at",
        }

        update_data = {
            field: value
            for field, value in changes.items()
            if field in allowed_fields
        }

        for field, value in update_data.items():
            setattr(profile, field, value)

        if update_data:
            profile.save(update_fields=[*update_data.keys(), "updated_at"])

        return profile
    
    @staticmethod
    def get_display_name(user: User) -> str:
        """
        Return the best display label for reminder messaging.
        """
        profile = ProfileService.get_or_create_profile(user)

        if profile.display_name:
            return profile.display_name

        if user.username:
            return user.username

        return user.email