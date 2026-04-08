from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from authentication.models.account_lockout import AccountLockout
from authentication.models.account_unlock_request import (
    AccountUnlockRequest,
)
from authentication.models.failed_login_attempts import FailedLoginAttempt
from authentication.models.otp_code import OTPCode
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.otp_service import OTPService
from authentication.services.token_service import TokenService
from core.urls.frontend_url import get_frontend_link

User = get_user_model()


class AccountUnlockService:
    """
    Handle unlock-account request and confirmation flows.
    """

    TOKEN_EXPIRY_MINUTES = 30
    OTP_EXPIRY_MINUTES = 10
    UNLOCK_PATH = "/auth/unlock-account"

    def __init__(self, user, website):
        if website is None:
            raise ValueError("Website context is required.")

        self.user = user
        self.website = website

    def _build_unlock_link(self, raw_token: str) -> str:
        return get_frontend_link(
            website=self.website,
            path=self.UNLOCK_PATH,
            query_params={"token": raw_token},
        )

    @transaction.atomic
    def create_unlock_request(
        self,
    ) -> tuple[AccountUnlockRequest, str, str, str]:
        AccountUnlockRequest.objects.filter(
            user=self.user,
            website=self.website,
            used_at__isnull=True,
        ).delete()

        raw_token, token_hash = TokenService.generate_hashed_token()

        unlock_request = AccountUnlockRequest.objects.create(
            user=self.user,
            website=self.website,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(
                minutes=self.TOKEN_EXPIRY_MINUTES,
            ),
        )

        otp_service = OTPService(
            user=self.user,
            website=self.website,
        )
        _otp_obj, raw_otp = otp_service.create_otp(
            purpose=OTPCode.Purpose.ACCOUNT_UNLOCK,
            expiry_minutes=self.OTP_EXPIRY_MINUTES,
        )

        unlock_link = self._build_unlock_link(raw_token)

        return unlock_request, raw_token, raw_otp, unlock_link

    @classmethod
    def request_unlock(
        cls,
        *,
        email: str,
        website,
    ) -> dict:
        user = User.objects.filter(
            email=email,
            website=website,
        ).first()

        if user is None:
            return {
                "success": True,
                "message": "If the account exists, unlock instructions were sent.",
            }

        service = cls(user=user, website=website)
        unlock_request, _raw_token, raw_otp, unlock_link = (
            service.create_unlock_request()
        )

        AuthNotificationBridgeService.send_account_unlock_notification(
            user=user,
            website=website,
            unlock_link=unlock_link,
            otp_code=raw_otp,
            expiry_minutes=service.TOKEN_EXPIRY_MINUTES,
        )

        return {
            "success": True,
            "request_id": unlock_request.pk,
            "message": "If the account exists, unlock instructions were sent.",
        }

    @transaction.atomic
    def confirm_unlock(
        self,
        *,
        raw_token: str,
        otp_code: str,
    ) -> dict:
        token_hash = TokenService.hash_value(raw_token)

        unlock_request = AccountUnlockRequest.objects.filter(
            user=self.user,
            website=self.website,
            token_hash=token_hash,
            used_at__isnull=True,
        ).first()

        if unlock_request is None or not unlock_request.is_valid:
            raise ValidationError("Invalid or expired unlock token.")

        otp_service = OTPService(
            user=self.user,
            website=self.website,
        )
        otp_service.consume_otp(
            purpose=OTPCode.Purpose.ACCOUNT_UNLOCK,
            raw_code=otp_code,
        )

        AccountLockout.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True,
        ).update(
            is_active=False,
            unlocked_at=timezone.now(),
        )

        FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website,
        ).delete()

        unlock_request.mark_as_used()

        if not self.user.is_active:
            self.user.is_active = True
            self.user.save(update_fields=["is_active"])

        AuthNotificationBridgeService.send_account_unlocked_notification(
            user=self.user,
            website=self.website,
        )

        return {
            "success": True,
            "message": "Account unlocked successfully.",
        }