from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.device_fingerprint_service import (
    DeviceFingerprintService,
)
from authentication.services.geo_service import GeoService
from authentication.services.login_security_service import (
    LoginSecurityService,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.session_limit_service import (
    SessionLimitService,
)
from authentication.services.security_event_service import (
    SecurityEventService,
)
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)
from authentication.models.security_events import SecurityEvent
from rest_framework_simplejwt.tokens import RefreshToken

class LoginFlowService:
    """
    Orchestrate the full login flow.
    """

    @classmethod
    def login(
        cls,
        *,
        email: str,
        password: str,
        request,
        website,
    ) -> dict:
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.headers.get("User-Agent", "")

        candidate_user = cls._get_candidate_user(
            email=email,
            website=website,
        )

        user = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if user is None:
            if candidate_user is not None:
                is_trusted = DeviceFingerprintService.is_trusted_device(
                    user=candidate_user,
                    website=website,
                    request=request,
                )

                geo = GeoService.get_geo(ip_address) if ip_address else {}

                LoginSecurityService.record_failed_login_and_enforce(
                    user=candidate_user,
                    website=website,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    city=geo.get("city"),
                    region=geo.get("region"),
                    country=geo.get("country"),
                    asn=geo.get("asn"),
                    is_trusted_device=is_trusted,
                )

            raise ValidationError("Invalid email or password.")

        if candidate_user is None or candidate_user.pk != user.pk:
            raise ValidationError("Invalid email or password.")

        LoginSecurityService.validate_login_allowed(
            user=user,
            website=website,
        )

        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )

        # Device fingerprinting and session limits are website-scoped.
        # Skip both for platform staff logging in without a website context.
        if website is not None:
            fingerprint = DeviceFingerprintService.resolve_or_create(
                user=user,
                website=website,
                request=request,
            )
            is_trusted_device = bool(fingerprint.is_trusted)
            fingerprint_device_name = getattr(fingerprint, "device_name", None)
            fingerprint_hash = getattr(fingerprint, "fingerprint_hash", None)
        else:
            is_trusted_device = True  # staff on their own portal are trusted
            fingerprint_device_name = None
            fingerprint_hash = None

        geo = GeoService.get_geo(ip_address) if ip_address else {}

        if cls._requires_mfa(
            user=user,
            is_trusted_device=is_trusted_device,
        ):
            return {
                "mfa_required": True,
                "user_id": user.pk,
            }

        session, _raw_session_token = LoginSessionService.start_session(
            user=user,
            website=website,
            ip=ip_address,
            user_agent=user_agent,
            device_info={"device_name": fingerprint_device_name},
            fingerprint_hash=fingerprint_hash,
        )
        refresh = RefreshToken.for_user(user)
        refresh["session_id"] = session.pk
        refresh["website_id"] = website.pk if website is not None else None

        if website is not None:
            SessionLimitService(
                user=user,
                website=website,
            ).enforce_session_limit(
                new_session=session,
                is_trusted_device=is_trusted_device,
            )

        location_parts = [
            geo.get("city"),
            geo.get("country"),
        ]
        location = ", ".join(
            [part for part in location_parts if part]
        ) or None

        SecurityEventService.log(
            user=user,
            website=website,
            event_type=SecurityEvent.EventType.LOGIN,
            severity=SecurityEvent.Severity.LOW,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            device=fingerprint_device_name,
            metadata={
                "session_id": session.pk,
                "trusted_device": is_trusted_device,
                "fingerprint_hash": fingerprint_hash,
            },
        )

        if not is_trusted_device and website is not None:
            AuthNotificationBridgeService.send_suspicious_login_notification(
                user=user,
                website=website,
                login_session=session,
                geo_location=location or "Unknown",
            )

        LoginSecurityService.record_successful_login(
            user=user,
            website=website,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {
            "success": True,
            "session_id": session.pk,
            "mfa_required": False,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    @staticmethod
    def _get_candidate_user(
        *,
        email: str,
        website,
    ):
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if website is not None:
            # Tenant-scoped lookup: user must belong to this website, OR be
            # a platform-level user (website=None) such as staff/admin.
            user = User.objects.filter(email=email, website=website).first()
            if user is None:
                user = User.objects.filter(email=email, website=None).first()
            return user

        # No website resolved (localhost / staff portal / unknown host):
        # find the user by email alone so all roles are reachable in dev
        # and from the staff/writer portal domains.
        return User.objects.filter(email=email).first()

    @staticmethod
    def _requires_mfa(
        *,
        user,
        is_trusted_device: bool,
    ) -> bool:
        """
        Keep this simple and aligned to your real MFA settings model.
        """
        mfa_settings = getattr(user, "mfa_settings", None)
        if mfa_settings is None:
            return False

        if not getattr(mfa_settings, "is_enabled", False):
            return False

        skip_on_trusted = getattr(
            mfa_settings,
            "skip_on_trusted",
            False,
        )
        if is_trusted_device and skip_on_trusted:
            return False

        return True