from django.db import transaction

from authentication.models.mfa_settings import MFASettings


class MFASettingsService:
    """
    Handle MFA settings retrieval and updates for a user within a
    website context.
    """

    @staticmethod
    @transaction.atomic
    def get_or_create_settings(*, user, website) -> tuple[MFASettings, bool]:
        """
        Retrieve or create MFA settings for a user and website.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            A tuple of:
                - MFASettings instance
                - whether the record was created
        """
        return MFASettings.objects.get_or_create(
            user=user,
            website=website,
        )

    @staticmethod
    @transaction.atomic
    def enable_mfa(
        *,
        user,
        website,
        preferred_method: str | None = None,
    ) -> MFASettings:
        """
        Enable MFA for a user.

        Args:
            user: User instance.
            website: Website instance.
            preferred_method: Optional preferred MFA method.

        Returns:
            Updated MFASettings instance.
        """
        settings_obj, _ = MFASettingsService.get_or_create_settings(
            user=user,
            website=website,
        )

        settings_obj.is_enabled = True

        if preferred_method is not None:
            settings_obj.preferred_method = preferred_method

        settings_obj.save(
            update_fields=["is_enabled", "preferred_method", "updated_at"]
        )

        return settings_obj

    @staticmethod
    @transaction.atomic
    def disable_mfa(
        *,
        user,
        website,
    ) -> MFASettings:
        """
        Disable MFA for a user.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            Updated MFASettings instance.
        """
        settings_obj, _ = MFASettingsService.get_or_create_settings(
            user=user,
            website=website,
        )

        settings_obj.is_enabled = False
        settings_obj.save(update_fields=["is_enabled", "updated_at"])

        return settings_obj

    @staticmethod
    @transaction.atomic
    def set_preferred_method(
        *,
        user,
        website,
        preferred_method: str,
    ) -> MFASettings:
        """
        Set the preferred MFA method for a user.

        Args:
            user: User instance.
            website: Website instance.
            preferred_method: Preferred MFA method value.

        Returns:
            Updated MFASettings instance.
        """
        settings_obj, _ = MFASettingsService.get_or_create_settings(
            user=user,
            website=website,
        )

        settings_obj.preferred_method = preferred_method
        settings_obj.save(
            update_fields=["preferred_method", "updated_at"]
        )

        return settings_obj

    @staticmethod
    @transaction.atomic
    def update_allowed_methods(
        *,
        user,
        website,
        allow_totp: bool | None = None,
        allow_email: bool | None = None,
        allow_sms: bool | None = None,
    ) -> MFASettings:
        """
        Update which MFA methods are allowed for a user.

        Args:
            user: User instance.
            website: Website instance.
            allow_totp: Optional TOTP allowance update.
            allow_email: Optional email MFA allowance update.
            allow_sms: Optional SMS MFA allowance update.

        Returns:
            Updated MFASettings instance.
        """
        settings_obj, _ = MFASettingsService.get_or_create_settings(
            user=user,
            website=website,
        )

        update_fields = ["updated_at"]

        if allow_totp is not None:
            settings_obj.allow_totp = allow_totp
            update_fields.append("allow_totp")

        if allow_email is not None:
            settings_obj.allow_email = allow_email
            update_fields.append("allow_email")

        if allow_sms is not None:
            settings_obj.allow_sms = allow_sms
            update_fields.append("allow_sms")

        settings_obj.save(update_fields=update_fields)

        return settings_obj