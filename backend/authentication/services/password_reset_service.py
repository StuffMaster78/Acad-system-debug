from datetime import timedelta
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from authentication.models.password_reset_request import (
    PasswordResetRequest,
)
from authentication.services.token_service import TokenService
from core.urls.frontend_url import get_frontend_link
from django.contrib.auth import get_user_model

from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.password_security_service import (
    PasswordSecurityService,
)
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)

class PasswordResetService:
    """
    Handle hybrid password reset workflows for a user within a website.
    """

    TOKEN_EXPIRATION_HOURS = 1
    RESET_PATH = "/auth/reset-password"

    def __init__(self, user, website):
        """
        Initialize the password reset service.

        Args:
            user: The user requesting the password reset.
            website: The tenant or website context.
        """
        self.user = user
        self.website = website

    def _build_reset_link(self, raw_token: str) -> str:
        """
        Build the frontend password reset link.

        Args:
            raw_token: Raw reset token.

        Returns:
            Fully qualified frontend reset URL.
        """
        return get_frontend_link(
            website=self.website,
            path=self.RESET_PATH,
            query_params={"token": raw_token},
        )

    def _get_valid_request_by_hash(
        self,
        *,
        field_name: str,
        hashed_value: str,
        invalid_message: str,
        expired_message: str,
    ) -> PasswordResetRequest:
        """
        Retrieve a valid password reset request by hashed credential.

        Args:
            field_name: Model field to query against.
            hashed_value: Hashed token or OTP value.
            invalid_message: Error raised when no matching request exists.
            expired_message: Error raised when the request is expired.

        Returns:
            A valid PasswordResetRequest instance.

        Raises:
            ValidationError: If the request is invalid, used, or expired.
        """
        filters = {
            "user": self.user,
            "website": self.website,
            field_name: hashed_value,
            "used_at__isnull": True,
        }

        try:
            reset_request = (
                PasswordResetRequest.objects
                .select_related("user", "website")
                .get(**filters)
            )
        except PasswordResetRequest.DoesNotExist as exc:
            raise ValidationError(invalid_message) from exc

        if not reset_request.is_valid:
            raise ValidationError(expired_message)

        return reset_request

    @transaction.atomic
    def create_reset_request(
        self,
    ) -> tuple[PasswordResetRequest, str, str, str]:
        """
        Create a new password reset request for the current user.

        Returns:
            A tuple containing:
                - the created PasswordResetRequest instance
                - the raw reset token
                - the raw OTP code
                - the frontend reset link
        """
        PasswordResetRequest.objects.filter(
            user=self.user,
            website=self.website,
            used_at__isnull=True,
        ).delete()

        raw_token, token_hash = TokenService.generate_hashed_token()
        raw_otp, otp_hash = TokenService.generate_hashed_otp()

        reset_request = PasswordResetRequest.objects.create(
            user=self.user,
            website=self.website,
            token_hash=token_hash,
            otp_hash=otp_hash,
            expires_at=TokenService.build_expiry(
                hours=self.TOKEN_EXPIRATION_HOURS,
            ),
        )

        reset_link = self._build_reset_link(raw_token)

        return reset_request, raw_token, raw_otp, reset_link

    def validate_token(
        self,
        raw_token: str,
    ) -> PasswordResetRequest:
        """
        Validate a reset token for the current user and website.
        """
        return self._get_valid_request_by_hash(
            field_name="token_hash",
            hashed_value=TokenService.hash_value(raw_token),
            invalid_message="Invalid or used reset token.",
            expired_message="Reset token has expired.",
        )

    def validate_otp(
        self,
        raw_otp: str,
    ) -> PasswordResetRequest:
        """
        Validate an OTP for the current user and website.
        """
        return self._get_valid_request_by_hash(
            field_name="otp_hash",
            hashed_value=TokenService.hash_value(raw_otp),
            invalid_message="Invalid or used OTP.",
            expired_message="OTP has expired.",
        )
    

    @classmethod
    def request_reset(
        cls,
        *,
        email: str,
        website,
        request=None,
    ) -> dict[str, Any]:
        """
        Create a password reset request for the user identified by email.

        This method is intentionally quiet when the user is not found,
        to avoid leaking account existence.

        Args:
            email: User email address.
            website: Website instance.
            request: Optional HTTP request object.

        Returns:
            Generic success response.
        """
        User = get_user_model()

        user = User.objects.filter(
            email=email,
            website=website,
        ).first()

        if user is None:
            return {"success": True}
        
        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )

        service = cls(user=user, website=website)
        reset_request, raw_token, raw_otp, reset_link = (
            service.create_reset_request()
        )

        AuthNotificationBridgeService.send_password_reset_notification(
            user=user,
            website=website,
            reset_link=reset_link,
            otp_code=raw_otp,
            expiry_hours=cls.TOKEN_EXPIRATION_HOURS,
        )

        return {
            "success": True,
            "request_id": reset_request.pk,
        }

    @classmethod
    @transaction.atomic
    def confirm_reset(
        cls,
        *,
        website,
        raw_token: str,
        otp_code: str,
        new_password: str,
    ) -> dict[str, Any]:
        """
        Complete a password reset after validating token and OTP.

        Args:
            website: Website instance.
            raw_token: Raw password reset token.
            otp_code: Raw OTP code.
            new_password: New password to set.

        Returns:
            Dictionary describing the reset result.

        Raises:
            ValidationError: If the token or OTP is invalid.
        """
        token_hash = TokenService.hash_value(raw_token)

        try:
            reset_request = PasswordResetRequest.objects.select_related(
                "user",
                "website",
            ).get(
                website=website,
                token_hash=token_hash,
                used_at__isnull=True,
            )
        except PasswordResetRequest.DoesNotExist as exc:
            raise ValidationError("Invalid or used reset token.") from exc

        if not reset_request.is_valid:
            raise ValidationError("Reset token has expired.")

        service = cls(user=reset_request.user, website=website)

        token_request = service.validate_token(raw_token)
        otp_request = service.validate_otp(otp_code)

        if token_request.pk != otp_request.pk:
            raise ValidationError(
                "Reset token and OTP do not belong to the same request."
            )

        AccountAccessPolicyService.validate_auth_access(
            user=reset_request.user,
            website=website,
        )
        PasswordSecurityService(
            user=reset_request.user,
            website=website,
        ).change_password(
            raw_password=new_password,
            context="password_reset",
            revoke_other_sessions=True,
            notify_user=True,
        )

        reset_request.used_at = timezone.now()
        reset_request.save(update_fields=["used_at"])

        return {
            "success": True,
            "request_id": reset_request.pk,
        }