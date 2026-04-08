from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    PermissionDenied,
    ValidationError,
)
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models.security_events import SecurityEvent
from authentication.models.login_session import LoginSession
from authentication.models.magic_links import MagicLink
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.device_fingerprint_service import (
    DeviceFingerprintService,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.security_event_service import (
    SecurityEventService,
)
from authentication.services.token_service import TokenService
from authentication.utils.ip import get_client_ip
from core.urls.frontend_url import get_frontend_link
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class MagicLinkService:
    """
    Handle passwordless authentication through magic links.

    This service is responsible for:
        - creating single-use magic links
        - validating submitted magic-link tokens
        - consuming magic links after successful use
        - creating authenticated user sessions

    Raw magic-link tokens must never be stored directly in the
    database if the model supports hashed token persistence.
    """

    DEFAULT_EXPIRY_MINUTES = 15
    MAGIC_LINK_PATH = "/auth/magic-link"

    def __init__(self, user, website, request=None):
        """
        Initialize the magic-link service.

        Args:
            website: The tenant or website context.
            request: Optional HTTP request object.
        """
        if website is None:
            raise ValueError(
                "Website context is required."
            )
        self.user = user
        self.website = website
        self.request = request

    def _build_magic_link(self, raw_token: str) -> str:
        """
        Build the frontend magic-link URL.

        Args:
            raw_token: Raw magic-link token.

        Returns:
            Fully qualified frontend magic-link URL.
        """
        return get_frontend_link(
            website=self.website,
            path=self.MAGIC_LINK_PATH,
            query_params={"token": raw_token},
        )

    def _get_user_by_email(self, email: str):
        """
        Retrieve an active user by email address.

        Args:
            email: User email address.

        Returns:
            The matched user instance.

        Raises:
            ValidationError: If the user does not exist or is inactive.
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as exc:
            raise ValidationError(
                "User not found with this email address."
            ) from exc

        if not user.is_active:
            raise ValidationError(
                "Account is disabled. Please contact support."
            )

        return user

    def _get_valid_magic_link(
        self,
        raw_token: str,
    ) -> MagicLink:
        """
        Retrieve a valid magic-link record by raw token.

        Args:
            raw_token: Raw token supplied by the user.

        Returns:
            A valid MagicLink instance.

        Raises:
            ValidationError: If the token is invalid, expired,
                or already used.
        """
        token_hash = TokenService.hash_value(raw_token)

        try:
            magic_link = (
                MagicLink.objects
                .select_related("user", "website")
                .get(
                    website=self.website,
                    token_hash=token_hash,
                    used_at__isnull=True,
                )
            )
        except MagicLink.DoesNotExist as exc:
            raise ValidationError(
                "Invalid or expired magic link. Please request a new one."
            ) from exc

        if not magic_link.is_valid:
            raise ValidationError(
                "Invalid or expired magic link. Please request a new one."
            )

        return magic_link

    @transaction.atomic
    def create_magic_link(
        self,
        *,
        created_by: str,
        email: str,
        expiry_minutes: int | None = None,
    ) -> tuple[MagicLink, str, str]:
        """
        Create a new magic link for the given email address.

        Any active magic links for the same user and website are removed
        before a new one is created.

        Args:
            email: User email address.
            expiry_minutes: Optional custom expiry duration in minutes.

        Returns:
            A tuple containing:
                - the created MagicLink instance
                - the raw magic-link token
                - the frontend magic-link URL
        """
        if expiry_minutes is None:
            expiry_minutes = self.DEFAULT_EXPIRY_MINUTES

        user = self._get_user_by_email(email)

        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=self.website,
        )

        MagicLink.objects.filter(
            user=user,
            website=self.website,
            used_at__isnull=True,
        ).delete()

        raw_token, token_hash = TokenService.generate_hashed_token()

        magic_link = MagicLink.objects.create(
            user=user,
            website=self.website,
            token_hash=token_hash,
            expires_at=TokenService.build_expiry(
                minutes=expiry_minutes,
            ),
            created_by=created_by,
            ip_address=(
                get_client_ip(self.request)
                if self.request
                else None
            ),
            user_agent=(
                self.request.headers.get("User-Agent", "")
                if self.request
                else ""
            ),
        )

        magic_url = self._build_magic_link(raw_token)

        return magic_link, raw_token, magic_url

    def build_notification_payload(
        self,
        *,
        email: str,
        magic_url: str,
        expiry_minutes: int | None = None,
    ) -> dict[str, Any]:
        """
        Build a notification payload for magic-link delivery.

        Args:
            email: Recipient email address.
            magic_url: Frontend magic-link URL.
            expiry_minutes: Optional custom expiry duration in minutes.

        Returns:
            A notification payload dictionary.
        """
        if expiry_minutes is None:
            expiry_minutes = self.DEFAULT_EXPIRY_MINUTES

        return {
            "to": email,
            "context": {
                "magic_url": magic_url,
                "expiry_minutes": expiry_minutes,
            },
        }

    @transaction.atomic
    def verify_magic_link(
        self,
        *,
        raw_token: str,
    ) -> dict[str, Any]:
        """
        Verify a magic link and authenticate the user.

        Args:
            raw_token: Raw token provided by the user.

        Returns:
            A dictionary containing access credentials, basic user
            information, and session identifier.

        Raises:
            ValidationError: If the token is invalid or the account
                is disabled.
        """
        magic_link = self._get_valid_magic_link(raw_token)
        user = magic_link.user

        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=self.website,
        )
        if not user.is_active:
            raise ValidationError(
                "Account is disabled. Please contact support."
            )

        magic_link.mark_as_used()

        refresh = RefreshToken.for_user(user)

        session = LoginSessionService.start_session(
            user=user,
            website=magic_link.website,
            ip=(
                get_client_ip(self.request)
                if self.request
                else None
            ),
            user_agent=(
                self.request.headers.get("User-Agent", "")
                if self.request
                else ""
            ),
            device_info={"type": "magic_link"},
        )

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": getattr(user, "username", ""),
                "role": getattr(user, "role", None),
            },
            "session_id": str(session.pk),
        }

    @classmethod
    def cleanup_stale_links(
        cls,
        *,
        days: int = 7,
    ) -> int:
        """
        Delete old magic-link records.

        Args:
            days: Age threshold in days.

        Returns:
            Number of deleted records.
        """
        cutoff = timezone.now() - timedelta(days=days)

        deleted_count, _ = MagicLink.objects.filter(
            created_at__lt=cutoff,
        ).delete()

        return deleted_count
    

    @classmethod
    def request_magic_link(
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
                "message": (
                    "If the account exists, a magic login link was sent."
                ),
            }

        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )

        service = cls(user=user, website=website)
        _magic_link, _raw_token, magic_url = service.create_magic_link(
            created_by=service.user,
            email=email,
            expiry_minutes=service.DEFAULT_EXPIRY_MINUTES,
        )

        AuthNotificationBridgeService.send_magic_link_notification(
            user=user,
            website=website,
            magic_url=magic_url,
            expiry_minutes=service.DEFAULT_EXPIRY_MINUTES,
        )

        return {
            "success": True,
            "message": (
                "If the account exists, a magic login link was sent."
            ),
        }

    @transaction.atomic
    def consume_magic_link(
        self,
        *,
        raw_token: str,
        request,
    ) -> dict:
        token_hash = TokenService.hash_value(raw_token)

        magic_link = MagicLink.objects.filter(
            user=self.user,
            website=self.website,
            token_hash=token_hash,
            used_at__isnull=True,
        ).first()

        if magic_link is None or not magic_link.is_valid:
            raise PermissionDenied("Invalid or expired magic link.")

        AccountAccessPolicyService.validate_auth_access(
            user=self.user,
            website=self.website,
        )

        fingerprint = DeviceFingerprintService.resolve_or_create(
            user=self.user,
            website=self.website,
            request=request,
        )

        session, _raw_session_token = LoginSessionService.start_session(
            user=self.user,
            website=self.website,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.headers.get("User-Agent", ""),
            device_info={
                "device_name": getattr(
                    fingerprint,
                    "device_name",
                    None,
                ),
            },
            session_type=LoginSession.SessionType.MAGIC_LINK,
            fingerprint_hash=getattr(
                fingerprint,
                "fingerprint_hash",
                None,
            ),
        )

        refresh = RefreshToken.for_user(self.user)
        refresh["session_id"] = session.pk
        refresh["website_id"] = self.website.pk

        magic_link.mark_as_used()

        SecurityEventService.log(
            user=self.user,
            website=self.website,
            event_type=SecurityEvent.EventType.MAGIC_LINK_USED,
            severity=SecurityEvent.Severity.LOW,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.headers.get("User-Agent", ""),
            device=getattr(fingerprint, "device_name", None),
            metadata={
                "session_id": session.pk,
                "fingerprint_hash": getattr(
                    fingerprint,
                    "fingerprint_hash",
                    None,
                ),
            },
        )

        return {
            "success": True,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "session_id": session.pk,
        }