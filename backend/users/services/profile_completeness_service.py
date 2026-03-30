from __future__ import annotations

from users.models.user import User


class ProfileCompletenessService:
    """
    Service for checking profile completeness.
    """

    @staticmethod
    def get_missing_fields(user: User) -> list[str]:
        """
        Return a list of missing profile-related fields for a user.
        """
        missing: list[str] = []

        if not user.phone_number:
            missing.append("phone_number")

        profile = getattr(user, "profile", None)
        if profile is not None:
            if not profile.display_name:
                missing.append("display_name")

        return missing

    @staticmethod
    def is_phone_missing(user: User) -> bool:
        """
        Return True if the user has no phone number.
        """
        return not bool(user.phone_number)

    @classmethod
    def is_profile_complete(cls, user: User) -> bool:
        """
        Return True if the tracked profile completeness checks pass.
        """
        return len(cls.get_missing_fields(user)) == 0