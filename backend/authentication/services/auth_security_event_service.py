from typing import Any

from authentication.models.audit import (
    AuthSecurityEvent, AuthEventType
)
from authentication.utils.audit import get_client_ip


class AuthSecurityEventService:
    @staticmethod
    def log_event(
        *,
        website,
        event_type: str,
        user=None,
        request=None,
        metadata: dict[str, Any] | None = None,
        device: str | None = None,
    ) -> AuthSecurityEvent:
        ip_address = get_client_ip(request) if request else None
        user_agent = (
            request.META.get("HTTP_USER_AGENT", "Unknown")
            if request
            else "Unknown"
        )
        resolved_device = (
            device
            or (
                request.META.get(
                    "HTTP_X_DEVICE",
                    "Unknown Device",
                )
                if request
                else "Unknown Device"
            )
        )

        return AuthSecurityEvent.objects.create(
            user=user,
            website=website,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            device=resolved_device,
            metadata=metadata or {},
        )

    @staticmethod
    def log_device_deletion(
        *,
        user,
        website,
        credential_id: str,
        request=None,
    ) -> AuthSecurityEvent:
        """
        Logs the action of deleting a registered device (WebAuthn credential).
        """
        return AuthSecurityEventService.log_event(
            user=user,
            website=website,
            event_type=AuthEventType.DEVICE_DELETED,
            request=request,
            metadata={"credential_id": credential_id},
        )

    @staticmethod
    def log_mfa_action(
        *,
        user,
        website,
        action: str,
        request=None,
        metadata: dict[str, Any] | None = None,
    ) -> AuthSecurityEvent:
        """
        Logs an MFA-related action with metadata.
        """
        return AuthSecurityEventService.log_event(
            user=user,
            website=website,
            event_type=action,
            request=request,
            metadata=metadata,
        )

    @staticmethod
    def log_qr_code_action(
        *,
        user,
        website,
        action: str,
        request=None,
        qr_code_data: str | None = None,
    ) -> AuthSecurityEvent:
        """
        Logs QR code related actions.
        """
        return AuthSecurityEventService.log_event(
            user=user,
            website=website,
            event_type=action,
            request=request,
            metadata={"qr_code_data": qr_code_data},
        )