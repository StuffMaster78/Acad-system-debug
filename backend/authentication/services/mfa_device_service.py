import pyotp
from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.mfa_device import MFADevice
from authentication.models.mfa_settings import MFASettings


class MFADeviceService:
    """
    Handle MFA device registration, verification, activation, and
    primary-device management.
    """

    @staticmethod
    def _validate_method_allowed(
        *,
        settings_obj: MFASettings,
        method: MFADevice.Method,
    ) -> None:
        """
        Validate that the requested MFA method is allowed.

        Args:
            settings_obj: MFA settings instance.
            method: MFA method value.

        Raises:
            ValidationError: If the method is not allowed.
        """
        allowed_map = {
            MFADevice.Method.TOTP: settings_obj.allow_totp,
            MFADevice.Method.EMAIL: settings_obj.allow_email,
            MFADevice.Method.SMS: settings_obj.allow_sms,
        }

        is_allowed = allowed_map.get(method)

        if not is_allowed:
            raise ValidationError("This MFA method is not allowed.")

    @staticmethod
    @transaction.atomic
    def register_device(
        *,
        user,
        website,
        method: MFADevice.Method,
        name: str,
        secret: str = "",
        phone_number: str = "",
        email: str = "",
        is_primary: bool = False,
    ) -> MFADevice:
        """
        Register a new MFA device for a user.

        Args:
            user: User instance.
            website: Website instance.
            method: MFA method value.
            name: Human-readable device name.
            secret: Optional TOTP secret.
            phone_number: Optional phone number for SMS MFA.
            email: Optional email for email-based MFA.
            is_primary: Whether the device should be primary.

        Returns:
            Created MFADevice instance.

        Raises:
            ValidationError: If the device method is not allowed.
        """
        settings_obj, _ = MFASettings.objects.get_or_create(
            user=user,
            website=website,
        )

        MFADeviceService._validate_method_allowed(
            settings_obj=settings_obj,
            method=method,
        )

        if is_primary:
            MFADevice.objects.filter(
                user=user,
                website=website,
                is_primary=True,
            ).update(is_primary=False)

        device = MFADevice.objects.create(
            user=user,
            website=website,
            method=method,
            name=name,
            secret=secret,
            phone_number=phone_number,
            email=email,
            is_primary=is_primary,
        )

        return device

    @staticmethod
    @transaction.atomic
    def mark_device_verified(
        *,
        device: MFADevice,
    ) -> MFADevice:
        """
        Mark an MFA device as verified.

        Args:
            device: MFADevice instance.

        Returns:
            Updated MFADevice instance.
        """
        device.mark_as_verified()
        return device

    @staticmethod
    @transaction.atomic
    def set_primary_device(
        *,
        device: MFADevice,
    ) -> MFADevice:
        """
        Set a device as the primary MFA device.

        Args:
            device: MFADevice instance.

        Returns:
            Updated MFADevice instance.
        """
        MFADevice.objects.filter(
            user=device.user,
            website=device.website,
            is_primary=True,
        ).exclude(pk=device.pk).update(is_primary=False)

        if not device.is_primary:
            device.is_primary = True
            device.save(update_fields=["is_primary", "updated_at"])

        return device

    @staticmethod
    @transaction.atomic
    def deactivate_device(
        *,
        device: MFADevice,
    ) -> MFADevice:
        """
        Deactivate an MFA device.

        Args:
            device: MFADevice instance.

        Returns:
            Updated MFADevice instance.
        """
        device.deactivate()
        return device

    @staticmethod
    @transaction.atomic
    def activate_device(
        *,
        device: MFADevice,
    ) -> MFADevice:
        """
        Activate an MFA device.

        Args:
            device: MFADevice instance.

        Returns:
            Updated MFADevice instance.
        """
        device.activate()
        return device

    @staticmethod
    def get_primary_device(
        *,
        user,
        website,
    ) -> MFADevice | None:
        """
        Retrieve the user's primary active MFA device.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            Primary MFADevice or None.
        """
        return MFADevice.objects.filter(
            user=user,
            website=website,
            is_primary=True,
            is_active=True,
        ).first()

    @staticmethod
    def get_verified_devices(
        *,
        user,
        website,
    ):
        """
        Retrieve verified active MFA devices for a user.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            QuerySet of verified active MFA devices.
        """
        return MFADevice.objects.filter(
            user=user,
            website=website,
            is_verified=True,
            is_active=True,
        )
    
    @staticmethod
    @transaction.atomic
    def verify_totp_device(
        *,
        device: MFADevice,
        code: str,
    ) -> MFADevice:
        """
        Verify a TOTP MFA device during setup.
        """
        if device.method != MFADevice.Method.TOTP:
            raise ValidationError("Only TOTP devices can be verified this way.")

        if not device.secret:
            raise ValidationError("Device secret is missing.")

        totp = pyotp.TOTP(device.secret)
        if not totp.verify(code):
            raise ValidationError("Invalid verification code.")

        device.mark_as_verified()
        return device