from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.mfa_device import MFADevice
from authentication.services.mfa_challenge_service import (
    MFAChallengeService,
)
from authentication.services.mfa_device_service import MFADeviceService
from authentication.services.mfa_settings_service import (
    MFASettingsService,
)
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)
from authentication.services.totp_service import TOTPService


class MFAOrchestrationService:
    """
    Coordinate MFA flows for authentication.

    This service determines whether MFA is required, selects the
    appropriate MFA device or method, issues OTP-based challenges
    where needed, and verifies submitted MFA codes.

    Responsibilities:
        - evaluate whether MFA is required for login
        - select the appropriate MFA device
        - initiate an MFA challenge or direct verification flow
        - verify submitted MFA codes
    """

    @staticmethod
    def get_settings(*, user, website):
        """
        Retrieve MFA settings for a user and website.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            MFASettings instance.
        """
        settings_obj, _ = MFASettingsService.get_or_create_settings(
            user=user,
            website=website,
        )
        return settings_obj

    @staticmethod
    def is_mfa_required(*, user, website) -> bool:
        """
        Determine whether MFA is required for the user.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            True if MFA is enabled and should be enforced,
            otherwise False.
        """
        settings_obj = MFAOrchestrationService.get_settings(
            user=user,
            website=website,
        )
        return bool(settings_obj.is_enabled or settings_obj.is_required)

    @staticmethod
    def get_available_devices(*, user, website):
        """
        Retrieve verified active MFA devices for the user.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            QuerySet of verified active MFA devices.
        """
        return MFADeviceService.get_verified_devices(
            user=user,
            website=website,
        )

    @staticmethod
    def get_preferred_device(*, user, website) -> MFADevice | None:
        """
        Retrieve the user's preferred MFA device.

        Preference order:
            1. Primary active verified device
            2. Device matching the preferred MFA method in settings
            3. First available active verified device

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            MFADevice instance or None if none are available.
        """
        primary_device = MFADeviceService.get_primary_device(
            user=user,
            website=website,
        )
        if primary_device is not None and primary_device.is_verified:
            return primary_device

        settings_obj = MFAOrchestrationService.get_settings(
            user=user,
            website=website,
        )

        if settings_obj.preferred_method:
            preferred_device = (
                MFADeviceService.get_verified_devices(
                    user=user,
                    website=website,
                )
                .filter(method=settings_obj.preferred_method)
                .first()
            )
            if preferred_device is not None:
                return preferred_device

        return MFADeviceService.get_verified_devices(
            user=user,
            website=website,
        ).first()

    @staticmethod
    @transaction.atomic
    def begin_mfa_for_login(
        *,
        user,
        website,
        request=None,
        device: MFADevice | None = None,
    ) -> dict[str, Any]:
        """
        Begin the MFA step for login.

        For TOTP devices, this returns an instruction for the client to
        prompt for an authenticator code.

        For email or SMS devices, this creates and returns an OTP-based
        challenge that can be delivered through the notification system.

        Args:
            user: User instance.
            website: Website instance.
            request: Optional HTTP request object.
            device: Optional explicit MFA device to use.

        Returns:
            A dictionary describing the next MFA step.

        Raises:
            ValidationError: If MFA is required but no usable device
                exists.
        """
        if not MFAOrchestrationService.is_mfa_required(
            user=user,
            website=website,
        ):
            return {
                "required": False,
                "status": "not_required",
            }

        selected_device = device or MFAOrchestrationService.get_preferred_device(
            user=user,
            website=website,
        )

        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )

        if selected_device is None:
            raise ValidationError(
                "MFA is required but no verified MFA device is available."
            )

        if not selected_device.is_active or not selected_device.is_verified:
            raise ValidationError(
                "The selected MFA device is not active and verified."
            )

        if selected_device.method == MFADevice.Method.TOTP:
            return {
                "required": True,
                "status": "challenge_required",
                "method": MFADevice.Method.TOTP,
                "device_id": selected_device.pk,
                "device_name": selected_device.name,
                "message": (
                    "Enter the code from your authenticator app."
                ),
            }

        challenge, raw_code = MFAChallengeService.create_challenge(
            user=user,
            website=website,
            device=selected_device,
            ip_address=(
                getattr(request, "META", {}).get("REMOTE_ADDR")
                if request
                else None
            ),
            user_agent=(
                request.headers.get("User-Agent", "")
                if request
                else None
            ),
        )

        return {
            "required": True,
            "status": "challenge_issued",
            "method": selected_device.method,
            "device_id": selected_device.pk,
            "device_name": selected_device.name,
            "challenge_id": challenge.pk,
            "delivery": {
                "email": selected_device.email,
                "phone_number": selected_device.phone_number,
            },
            "raw_code": raw_code,
        }

    @staticmethod
    @transaction.atomic
    def verify_login_mfa(
        *,
        user,
        website,
        code: str,
        device: MFADevice | None = None,
        device_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Verify the submitted MFA code for login.

        For TOTP devices, the code is verified directly against the
        device secret.

        For email or SMS devices, the code is verified against an
        issued MFA challenge.

        Args:
            user: User instance.
            website: Website instance.
            code: Submitted MFA code.
            device: Optional MFADevice instance.
            device_id: Optional explicit device ID.

        Returns:
            A dictionary describing the verification result.

        Raises:
            ValidationError: If no suitable device is found or the
                submitted code is invalid.
        """
        selected_device = device

        if selected_device is None and device_id is not None:
            selected_device = MFADevice.objects.filter(
                user=user,
                website=website,
                pk=device_id,
                is_active=True,
            ).first()

        if selected_device is None:
            selected_device = MFAOrchestrationService.get_preferred_device(
                user=user,
                website=website,
            )

        if selected_device is None:
            raise ValidationError(
                "No MFA device is available for verification."
            )

        if selected_device.method == MFADevice.Method.TOTP:
            TOTPService.authenticate_with_totp(
                device=selected_device,
                code=code,
            )
            return {
                "verified": True,
                "method": MFADevice.Method.TOTP,
                "device_id": selected_device.pk,
                "device_name": selected_device.name,
            }

        challenge = MFAChallengeService.verify_challenge(
            user=user,
            website=website,
            device=selected_device,
            raw_code=code,
        )

        return {
            "verified": True,
            "method": selected_device.method,
            "device_id": selected_device.pk,
            "device_name": selected_device.name,
            "challenge_id": challenge.pk,
        }

    @staticmethod
    def get_login_state(*, user, website) -> dict[str, Any]:
        """
        Return the MFA state for the user's login flow.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            A dictionary describing whether MFA is required and what
            methods or devices are available.
        """
        settings_obj = MFAOrchestrationService.get_settings(
            user=user,
            website=website,
        )
        devices = MFAOrchestrationService.get_available_devices(
            user=user,
            website=website,
        )

        return {
            "required": bool(
                settings_obj.is_enabled or settings_obj.is_required
            ),
            "preferred_method": settings_obj.preferred_method,
            "available_methods": list(
                devices.values_list("method", flat=True).distinct()
            ),
            "device_count": devices.count(),
        }