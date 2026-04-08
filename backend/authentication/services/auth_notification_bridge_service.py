from typing import Any

from notifications_system.services.notification_service import (
    NotificationService,
)
from core.urls.frontend_url import build_frontend_url


class AuthNotificationBridgeService:
    """
    Bridge authentication workflows to the central notification system.

    This service is responsible for converting internal authentication
    workflow outputs into notification payloads and dispatching them
    through the central notification layer.

    Sensitive values such as raw OTPs and raw reset tokens should be
    handled here and must never be exposed in public API responses.
    """

    @staticmethod
    def send_password_reset_notification(
        *,
        user,
        website,
        reset_link: str,
        otp_code: str,
        expiry_hours: int,
    ) -> None:
        """
        Send a password reset notification.

        Args:
            user: User receiving the password reset message.
            website: Website or tenant context.
            reset_link: Frontend password reset link.
            otp_code: Raw OTP code for fallback reset verification.
            expiry_hours: Password reset expiry duration in hours.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.password_reset_requested",
            context={
                "user": user,
                "reset_link": reset_link,
                "otp_code": otp_code,
                "expiry_hours": expiry_hours,
            },
        )

    @staticmethod
    def send_magic_link_notification(
        *,
        user,
        website,
        magic_url: str,
        expiry_minutes: int,
    ) -> None:
        """
        Send a magic-link login notification.

        Args:
            user: User receiving the magic-link email.
            website: Website or tenant context.
            magic_url: Frontend magic-link URL.
            expiry_minutes: Magic-link expiry duration in minutes.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.magic_link_requested",
            context={
                "user": user,
                "magic_url": magic_url,
                "expiry_minutes": expiry_minutes,
            },
        )

    @staticmethod
    def send_mfa_challenge_notification(
        *,
        user,
        website,
        device_method: str,
        raw_code: str,
        device_name: str,
        expiry_minutes: int,
        email: str = "",
        phone_number: str = "",
    ) -> None:
        """
        Send an MFA challenge notification for email or SMS delivery.

        Args:
            user: User receiving the MFA challenge.
            website: Website or tenant context.
            device_method: MFA method used for delivery.
            raw_code: Raw OTP challenge code.
            device_name: Human-readable MFA device name.
            expiry_minutes: Challenge expiry duration in minutes.
            email: Optional destination email.
            phone_number: Optional destination phone number.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.mfa_challenge_requested",
            context={
                "user": user,
                "otp_code": raw_code,
                "device_name": device_name,
                "device_method": device_method,
                "expiry_minutes": expiry_minutes,
                "email": email,
                "phone_number": phone_number,
            },
        )

    @staticmethod
    def build_safe_mfa_response(
        *,
        method: str,
        device_id: int,
        device_name: str,
        challenge_id: int | None = None,
        email: str = "",
        phone_number: str = "",
    ) -> dict[str, Any]:
        """
        Build a safe MFA response payload for API consumers.

        Args:
            method: MFA method value.
            device_id: MFA device ID.
            device_name: Human-readable device name.
            challenge_id: Optional issued challenge ID.
            email: Optional destination email.
            phone_number: Optional destination phone number.

        Returns:
            A safe response payload without sensitive codes.
        """
        return {
            "required": True,
            "status": "challenge_issued",
            "method": method,
            "device_id": device_id,
            "device_name": device_name,
            "challenge_id": challenge_id,
            "delivery": {
                "email": AuthNotificationBridgeService._mask_email(
                    email
                ) if email else "",
                "phone_number": (
                    AuthNotificationBridgeService._mask_phone_number(
                        phone_number
                    )
                    if phone_number
                    else ""
                ),
            },
        }

    @staticmethod
    def _mask_email(email: str) -> str:
        """
        Mask an email address for safe display.

        Args:
            email: Email address to mask.

        Returns:
            Masked email string.
        """
        if "@" not in email:
            return email

        local_part, domain = email.split("@", 1)

        if len(local_part) <= 2:
            masked_local = local_part[0] + "*"
        else:
            masked_local = local_part[0] + "***" + local_part[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def _mask_phone_number(phone_number: str) -> str:
        """
        Mask a phone number for safe display.

        Args:
            phone_number: Phone number to mask.

        Returns:
            Masked phone number string.
        """
        if len(phone_number) <= 4:
            return "*" * len(phone_number)

        return "*" * (len(phone_number) - 4) + phone_number[-4:]
    


    @staticmethod
    def send_account_lockout_notification(
        *,
        user,
        website,
        reason: str,
        duration_minutes: int,
    ) -> None:
        """
        Send an account lockout notification.

        Args:
            user: Locked-out user.
            website: Website or tenant context.
            reason: Lockout reason.
            duration_minutes: Lockout duration in minutes.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.account_lockout",
            context={
                "user": user,
                "reason": reason,
                "duration_minutes": duration_minutes,
            },
            channels=["email", "in_app"],
            priority="high",
        )

    # Helper Methods to build frontend URL
    @staticmethod
    def build_email_change_verification_url(*, raw_token: str) -> str:
        """
        Build the frontend URL for verifying the new email address.
        """
        return build_frontend_url(
            path="/verify-email-change",
            query_params={"token": raw_token},
        )

    @staticmethod
    def build_email_change_old_email_confirmation_url(
        *,
        raw_token: str,
    ) -> str:
        """
        Build the frontend URL for confirming the old email address.
        """
        return build_frontend_url(
            path="/confirm-email-change",
            query_params={"token": raw_token},
        )

    def build_password_reset_url(
        *,
        token: str,
    ) -> str:
        """
        Build URL for password reset flow.
        """
        return build_frontend_url(
            path="/reset-password",
            query_params={"token": token},
        )


    def build_magic_link_url(
        *,
        token: str,
    ) -> str:
        """
        Build URL for magic link authentication.
        """
        return build_frontend_url(
            path="/magic-login",
            query_params={"token": token},
        )

    @staticmethod
    def send_email_change_admin_review_notification(
        *,
        user,
        website,
        old_email: str,
        new_email: str,
        request_id: int,
        expires_at,
    ) -> None:
        """
        Notify admins that a user has requested an email change.

        Args:
            user: User requesting the email change.
            website: Website or tenant context.
            old_email: Current email address.
            new_email: Requested new email address.
            request_id: Email change request ID.
            expires_at: Request expiry datetime.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.email_change_requested_admin_review",
            context={
                "user": user,
                "old_email": old_email,
                "new_email": new_email,
                "request_id": request_id,
                "expires_at": expires_at,
            },
            priority="normal",
            channels=["email", "in_app"],
        )

    @staticmethod
    def send_email_change_new_email_verification(
        *,
        user,
        website,
        new_email: str,
        verification_url: str,
        expires_hours: int,
    ) -> None:
        """
        Send verification instructions to the new email address.

        Args:
            user: User requesting the email change.
            website: Website or tenant context.
            new_email: New email address to verify.
            verification_url: Frontend verification URL.
            expires_hours: Token expiry duration in hours.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.email_change_verify_new_email",
            context={
                "user": user,
                "new_email": new_email,
                "verification_url": verification_url,
                "expires_hours": expires_hours,
            },
            channels=["email", "in_app"],
            priority="normal"
        )

    @staticmethod
    def send_email_change_old_email_confirmation(
        *,
        user,
        website,
        old_email: str,
        new_email: str,
        confirmation_url: str,
        expires_hours: int,
    ) -> None:
        """
        Send confirmation instructions to the old email address.

        Args:
            user: User requesting the email change.
            website: Website or tenant context.
            old_email: Current email address.
            new_email: Requested new email address.
            confirmation_url: Frontend old-email confirmation URL.
            expires_hours: Token expiry duration in hours.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.email_change_confirm_old_email",
            context={
                "user": user,
                "old_email": old_email,
                "new_email": new_email,
                "confirmation_url": confirmation_url,
                "expires_hours": expires_hours,
            },
            priority="normal",
            channels=["email", "in_app"],
        )

    @staticmethod
    def send_email_change_rejection_notification(
        *,
        user,
        website,
        rejection_reason: str,
    ) -> None:
        """
        Notify the user that the email change request was rejected.

        Args:
            user: User whose request was rejected.
            website: Website or tenant context.
            rejection_reason: Reason for rejection.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.email_change_rejected",
            context={
                "user": user,
                "rejection_reason": rejection_reason,
            },
            channels=["in_app", "email"],
            priority="normal",
        )

    @staticmethod
    def send_email_change_completed_notification(
        *,
        user,
        website,
        old_email: str,
        new_email: str,
    ) -> None:
        """
        Notify the user that the email address was changed successfully.

        Args:
            user: User whose email was changed.
            website: Website or tenant context.
            old_email: Previous email address.
            new_email: New email address.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.email_change_completed",
            context={
                "user": user,
                "old_email": old_email,
                "new_email": new_email,
            },
            priority="normal",
            channels=["email", "in_app"],
        )

    @staticmethod
    def send_phone_verification_notification(
        *,
        user,
        website,
        phone_number: str,
        raw_code: str,
        expiry_minutes: int,
    ) -> None:
        """
        Send a phone verification challenge.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.phone_verification_requested",
            context={
                "user": user,
                "phone_number": phone_number,
                "otp_code": raw_code,
                "expiry_minutes": expiry_minutes,
            },
            priority="normal",
            channels=["email", "in_app"],
        )


    @staticmethod
    def send_account_deletion_scheduled_notification(
        *,
        user,
        website,
        undo_url: str,
        expiry_hours: int,
        reason: str = "",
    ) -> None:
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.account_deletion_scheduled",
            context={
                "user": user,
                "undo_url": undo_url,
                "expiry_hours": expiry_hours,
                "reason": reason,
            },
            channels=["email", "in_app"],
        )


    @staticmethod
    def send_account_deletion_cancelled_notification(
        *,
        user,
        website,
    ) -> None:
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.account_deletion_cancelled",
            context={
                "user": user,
            },
            channels=["email", "in_app"],
        )


    @staticmethod
    def send_account_deletion_completed_notification(
        *,
        user,
        website,
    ) -> None:
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.account_deletion_completed",
            context={
                "user": user,
            },
            channels=["email", "in_app"],
        )


    @staticmethod
    def send_registration_verification_notification(
        *,
        user,
        website,
        verification_link: str,
        raw_token: str,
        expiry_minutes: int,
    ) -> None:
        """
        Send registration verification email.

        Args:
            user: User receiving the verification message.
            website: Website or tenant context.
            verification_link: Frontend verification link.
            raw_token: Raw OTP code for fallback verification.
            expiry_minutes: Verification expiry duration in minutes.
        """

        verification_url = build_frontend_url(
            path="/register/verify",
            query_params={"token": raw_token},
        )

        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.registration_verification_requested",
            context={
                "user": user,
                "verification_url": verification_url,
                "otp_code": raw_token,
                "expiry_minutes": expiry_minutes,
            },
            channels=["email", "in_app"],
            priority="high",
        )

    @staticmethod
    def send_account_unlock_notification(
        *,
        user,
        website,
        unlock_link: str,
        otp_code: str,
        expiry_minutes: int = 30,
    ) -> None:
        """
        Send account unlock notification with a secure confirmation link.

        Args:
            user: User whose account is being unlocked.
            website: Website or tenant context.
            raw_token: Raw unlock token.
            expiry_minutes: Token expiry in minutes.
        """
        unlock_link = build_frontend_url(
            path="/unlock-account/confirm",
            query_params={"token": otp_code},
        )

        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.account_unlock_requested",
            context={
                "user": user,
                "unlock_url": unlock_link,
                "otp_code": otp_code,
                "expiry_minutes": expiry_minutes,
            },
            channels=["email", "in_app"],
        )

    @staticmethod
    def send_suspicious_login_notification(
        *,
        user,
        website,
        login_session,
        geo_location: str = "Unknown",
    ) -> None:
        """
        Send suspicious login notification to the user.
        """
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.suspicious_login_detected",
            context={
                "user": user,
                "ip_address": login_session.ip_address,
                "user_agent": login_session.user_agent,
                "timestamp": login_session.logged_in_at,
                "geo_location": geo_location,
                "session_id": login_session.pk,
                "session_type": login_session.session_type,
            },
            channels=["email", "in_app"],
        )
    
    # @staticmethod
    # def send_registration_verification_notification(
    #     *,
    #     user,
    #     website,
    #     verification_link: str,
    #     otp_code: str,
    #     expiry_minutes: int,
    # ) -> None:
    #     NotificationService.notify(
    #         recipient=user,
    #         website=website,
    #         event_key="auth.registration_verification_requested",
    #         context={
    #             "user": user,
    #             "verification_link": verification_link,
    #             "otp_code": otp_code,
    #             "expiry_minutes": expiry_minutes,
    #         },
    #     )

    # @staticmethod
    # def send_password_reset_notification(
    #     *,
    #     user,
    #     website,
    #     reset_link: str,
    #     otp_code: str,
    #     expiry_hours: int,
    # ) -> None:
    #     NotificationService.notify(
    #         recipient=user,
    #         website=website,
    #         event_key="auth.password_reset_requested",
    #         context={
    #             "user": user,
    #             "reset_link": reset_link,
    #             "otp_code": otp_code,
    #             "expiry_hours": expiry_hours,
    #         },
    #     )

    # @staticmethod
    # def send_account_unlock_notification(
    #     *,
    #     user,
    #     website,
    #     unlock_link: str,
    #     otp_code: str,
    #     expiry_minutes: int,
    # ) -> None:
    #     NotificationService.notify(
    #         recipient=user,
    #         website=website,
    #         event_key="auth.account_unlock_requested",
    #         context={
    #             "user": user,
    #             "unlock_link": unlock_link,
    #             "otp_code": otp_code,
    #             "expiry_minutes": expiry_minutes,
    #         },
    #     )

    @staticmethod
    def send_account_unlocked_notification(
        *,
        user,
        website,
    ) -> None:
        NotificationService.notify(
            recipient=user,
            website=website,
            event_key="auth.account_unlocked",
            context={
                "user": user,
            },
        )


    # @staticmethod
    # def send_magic_link_notification(
    #     *,
    #     user,
    #     website,
    #     magic_url: str,
    #     expiry_minutes: int,
    # ) -> None:
    #     NotificationService.notify(
    #         recipient=user,
    #         website=website,
    #         event_key="auth.magic_link_requested",
    #         context={
    #             "user": user,
    #             "magic_url": magic_url,
    #             "expiry_minutes": expiry_minutes,
    #         },
    #     )