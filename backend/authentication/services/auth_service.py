from typing import Any

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.services.login_security_service import (
    LoginSecurityService,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.mfa_orchestration_service import (
    MFAOrchestrationService,
)
from authentication.utils.ip import get_client_ip
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService
)
from authentication.services.mfa_challenge_service import (
    MFAChallengeService
)
from authentication.services.device_fingerprint_service import (
    DeviceFingerprintService
)
from authentication.services.device_security_alert_service import (
    DeviceSecurityAlertService
)
from authentication.models.mfa_device import MFADevice

from authentication.services.account_suspension_service import (
    AccountSuspensionService
)


class AuthenticationService:
    """
    Handle top-level authentication workflows.

    This service coordinates the login process by:
        - validating credentials
        - enforcing access gates
        - checking lockout policy
        - deciding whether MFA is required
        - creating authenticated sessions when login succeeds

    Lower-level responsibilities such as session creation, failed-login
    tracking, and MFA challenges are delegated to dedicated services.
    """
    @classmethod
    def _should_force_mfa_for_risk(
        cls,
        *,
        user,
        website,
        request=None,
    ) -> bool:
        """
        Determine whether MFA should be forced based on device
        fingerprint risk.

        Args:
            user: User instance.
            website: Website or tenant context.
            request: Optional HTTP request object.

        Returns:
            True if MFA should be forced for this login attempt,
            otherwise False.
        """
        fingerprint_data = cls._extract_fingerprint_data(request)

        if fingerprint_data is None:
            return False

        raw_fingerprint_data = fingerprint_data.get(
            "raw_fingerprint_data",
        )
        if not raw_fingerprint_data:
            return False

        fingerprint_service = DeviceFingerprintService(
            user=user,
            website=website,
        )

        try:
            fingerprint_hash = fingerprint_service.hash_fingerprint_data(
                raw_fingerprint_data,
            )
        except ValueError:
            return False

        risk_result = fingerprint_service.evaluate_risk(
            fingerprint_hash=fingerprint_hash,
        )

        return bool(risk_result["is_high_risk"])
    
    @classmethod
    def _get_login_risk_context(
        cls,
        *,
        user,
        website,
        request=None,
    ) -> dict[str, Any]:
        """
        Build risk context for the current login request.

        Args:
            user: User instance.
            website: Website or tenant context.
            request: Optional HTTP request object.

        Returns:
            A dictionary containing fingerprint hash, risk score,
            and whether MFA should be forced.
        """
        fingerprint_data = cls._extract_fingerprint_data(request)

        if fingerprint_data is None:
            return {
                "fingerprint_hash": None,
                "score": 0.0,
                "is_high_risk": False,
            }

        raw_fingerprint_data = fingerprint_data.get(
            "raw_fingerprint_data",
        )
        if not raw_fingerprint_data:
            return {
                "fingerprint_hash": None,
                "score": 0.0,
                "is_high_risk": False,
            }

        fingerprint_service = DeviceFingerprintService(
            user=user,
            website=website,
        )

        try:
            fingerprint_hash = fingerprint_service.hash_fingerprint_data(
                raw_fingerprint_data,
            )
        except ValueError:
            return {
                "fingerprint_hash": None,
                "score": 0.0,
                "is_high_risk": False,
            }

        risk_result = fingerprint_service.evaluate_risk(
            fingerprint_hash=fingerprint_hash,
        )

        return {
            "fingerprint_hash": fingerprint_hash,
            "score": float(risk_result["score"]),
            "is_high_risk": bool(risk_result["is_high_risk"]),
        }
    
    @classmethod
    def _is_trusted_device_for_request(
        cls,
        *,
        user,
        website,
        request=None,
    ) -> bool:
        """
        Determine whether the current request comes from a trusted
        device fingerprint.

        Args:
            user: User instance.
            website: Website or tenant context.
            request: Optional HTTP request object.

        Returns:
            True if the request fingerprint matches a trusted
            fingerprint record, otherwise False.
        """
        fingerprint_data = cls._extract_fingerprint_data(request)

        if fingerprint_data is None:
            return False

        raw_fingerprint_data = fingerprint_data.get(
            "raw_fingerprint_data",
        )
        if not raw_fingerprint_data:
            return False

        fingerprint_service = DeviceFingerprintService(
            user=user,
            website=website,
        )

        try:
            fingerprint_hash = fingerprint_service.hash_fingerprint_data(
                raw_fingerprint_data,
            )
        except ValueError:
            return False

        fingerprint = fingerprint_service.get_fingerprint_by_hash(
            fingerprint_hash=fingerprint_hash,
        )

        if fingerprint is None:
            return False

        return bool(fingerprint.is_trusted)
    
    @staticmethod
    def _extract_fingerprint_data(
        request,
    ) -> dict[str, Any] | None:
        """
        Extract fingerprint-related data from the request.

        Args:
            request: HTTP request object.

        Returns:
            Fingerprint payload dictionary, or None if fingerprint
            data is unavailable.
        """
        if request is None:
            return None

        raw_fingerprint_data = request.headers.get(
            "X-Device-Fingerprint",
        )

        if not raw_fingerprint_data:
            return None

        return {
            "raw_fingerprint_data": raw_fingerprint_data,
            "user_agent": request.headers.get("User-Agent", ""),
            "ip_address": get_client_ip(request),
        }

    @staticmethod
    def _get_user_agent(request) -> str:
        """
        Extract the user agent string from a request.

        Args:
            request: HTTP request object.

        Returns:
            User agent string, or an empty string if unavailable.
        """
        if request is None:
            return ""

        return request.headers.get("User-Agent", "")

    @staticmethod
    def _get_device_info(request) -> dict[str, Any]:
        """
        Build device information from the request.

        Args:
            request: HTTP request object.

        Returns:
            Dictionary containing basic device metadata.
        """
        if request is None:
            return {}

        return {
            "user_agent": request.headers.get("User-Agent", ""),
            "device": request.headers.get("X-Device", ""),
        }

    @staticmethod
    def _check_access_gates(user) -> None:
        """
        Enforce account-level access gates before login.

        Args:
            user: Authenticated user instance.

        Raises:
            ValidationError: If the account is not allowed to log in.
        """
        if not user.is_active:
            raise ValidationError(
                "This account is disabled. Please contact support."
            )

    @classmethod
    def login_with_password(
        cls,
        *,
        email: str,
        password: str,
        website,
        request=None,
    ) -> dict[str, Any]:
        """
        Authenticate a user with email and password.

        Flow:
            1. Check lockout status
            2. Authenticate credentials
            3. Record failed attempts if authentication fails
            4. Enforce access gates
            5. Decide whether MFA is required
            6. If MFA is not required, create session and issue tokens

        Args:
            email: User email address.
            password: Submitted password.
            website: Tenant or website context.
            request: Optional HTTP request object.

        Returns:
            A dictionary describing the next authentication step.

            On direct success:
                {
                    "authenticated": True,
                    "mfa_required": False,
                    "access": "...",
                    "refresh": "...",
                    "session_id": "...",
                    "user": {...},
                }

            On MFA-required:
                {
                    "authenticated": False,
                    "mfa_required": True,
                    "mfa": {...},
                    "user_id": ...,
                }

        Raises:
            ValidationError: If credentials are invalid or the account
                is locked out or inactive.
        """
        ip_address = get_client_ip(request) if request else None
        user_agent = cls._get_user_agent(request)

        if LoginSecurityService.is_ip_blocked(
            website=website,
            ip_address=ip_address,
        ):
            raise ValidationError(
                "This IP address is temporarily blocked. Please try again later."
            )

        candidate_user = LoginSecurityService.get_user_by_email(
            email=email,
        )

        if candidate_user is not None:
            active_lockout = LoginSecurityService.get_active_lockout(
                user=candidate_user,
                website=website,
            )
            if active_lockout is not None:
                raise ValidationError(
                    active_lockout.reason
                    or "This account is temporarily locked."
                )

        user = authenticate(
            request=request,
            username=email,
            password=password,
        )

        if user is None:
            if candidate_user is not None:
                is_trusted_device = cls._is_trusted_device_for_request(
                    user=candidate_user,
                    website=website,
                    request=request,
                )

                LoginSecurityService.record_failed_login_and_enforce(
                    user=candidate_user,
                    website=website,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_trusted_device=is_trusted_device,
                )

            raise ValidationError("Invalid email or password.")
        
        suspension_service = AccountSuspensionService(
            user=candidate_user,
            website=website,
        )
        if suspension_service.is_suspended():
            raise ValidationError(
                "This account is suspended for this website."
            )

        cls._check_access_gates(user)

        LoginSecurityService.clear_failed_logins(
            user=user,
            website=website,
        )

        policy_requires_mfa = MFAOrchestrationService.is_mfa_required(
            user=user,
            website=website,
        )

        risk_context = cls._get_login_risk_context(
            user=user,
            website=website,
            request=request,
        )

        risk_requires_mfa = risk_context["is_high_risk"]

        if (
            risk_requires_mfa
            and risk_context["fingerprint_hash"]
        ):
            DeviceSecurityAlertService.evaluate_and_alert_if_risky(
                user=user,
                website=website,
                fingerprint_service=DeviceFingerprintService(
                    user=user,
                    website=website,
                ),
                fingerprint_hash=risk_context["fingerprint_hash"],
                ip_address=ip_address,
                metadata={
                    "stage": "pre_mfa_login",
                    "email": email,
                },
            )

        if policy_requires_mfa or risk_requires_mfa:
            mfa_result = MFAOrchestrationService.begin_mfa_for_login(
                user=user,
                website=website,
                request=request,
            )

            if mfa_result["method"] in {
                MFADevice.Method.EMAIL,
                MFADevice.Method.SMS,
            }:
                AuthNotificationBridgeService.send_mfa_challenge_notification(
                    user=user,
                    website=website,
                    device_method=mfa_result["method"],
                    raw_code=mfa_result["raw_code"],
                    device_name=mfa_result["device_name"],
                    expiry_minutes=MFAChallengeService.DEFAULT_EXPIRY_MINUTES,
                    email=mfa_result["delivery"].get("email", ""),
                    phone_number=mfa_result["delivery"].get(
                        "phone_number",
                        "",
                    ),
                )

            safe_mfa_response = (
                AuthNotificationBridgeService.build_safe_mfa_response(
                    method=mfa_result["method"],
                    device_id=mfa_result["device_id"],
                    device_name=mfa_result["device_name"],
                    challenge_id=mfa_result.get("challenge_id"),
                    email=mfa_result["delivery"].get("email", ""),
                    phone_number=mfa_result["delivery"].get(
                        "phone_number",
                        "",
                    ),
                )
            )

            return {
                "authenticated": False,
                "mfa_required": True,
                "mfa_reason": (
                    "risk_based"
                    if risk_requires_mfa and not policy_requires_mfa
                    else "policy"
                ),
                "mfa": safe_mfa_response,
                "user_id": user.pk,
                "risk": {
                    "is_high_risk": risk_requires_mfa,
                    "score": risk_context["score"],
                },
            }

        refresh = RefreshToken.for_user(user)

        session = LoginSessionService.start_session(
            user=user,
            website=website,
            ip=ip_address,
            user_agent=user_agent,
            device_info=cls._get_device_info(request),
        )

        cls._handle_device_fingerprint(
            user=user,
            website=website,
            request=request,
        )

        return {
            "authenticated": True,
            "mfa_required": False,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "session_id": str(session.pk),
            "user": {
                "id": user.pk,
                "email": getattr(user, "email", ""),
                "username": getattr(user, "username", ""),
                "role": getattr(user, "role", None),
            },
        }

    @classmethod
    def complete_mfa_login(
        cls,
        *,
        user,
        website,
        code: str,
        request=None,
        device_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Complete a login flow after MFA verification.

        Args:
            user: User instance.
            website: Tenant or website context.
            code: Submitted MFA code.
            request: Optional HTTP request object.
            device_id: Optional MFA device ID.

        Returns:
            A dictionary containing authentication tokens, session data,
            and user information.

        Raises:
            ValidationError: If MFA verification fails or access is
                denied.
        """
        cls._check_access_gates(user)

        MFAOrchestrationService.verify_login_mfa(
            user=user,
            website=website,
            code=code,
            device_id=device_id,
        )

        refresh = RefreshToken.for_user(user)
        ip_address = get_client_ip(request) if request else None
        user_agent = cls._get_user_agent(request)

        session = LoginSessionService.start_session(
            user=user,
            website=website,
            ip=ip_address,
            user_agent=user_agent,
            device_info=cls._get_device_info(request),
        )

        cls._handle_device_fingerprint(
            user=user,
            website=website,
            request=request,
        )

        return {
            "authenticated": True,
            "mfa_required": False,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "session_id": str(session.pk),
            "user": {
                "id": user.pk,
                "email": getattr(user, "email", ""),
                "username": getattr(user, "username", ""),
                "role": getattr(user, "role", None),
            },
        }
    
    @classmethod
    def _handle_device_fingerprint(
        cls,
        *,
        user,
        website,
        request=None,
    ) -> None:
        """
        Process device fingerprint updates and suspicious activity
        checks after a successful authentication event.

        Args:
            user: Authenticated user instance.
            website: Website or tenant context.
            request: Optional HTTP request object.
        """
        fingerprint_data = cls._extract_fingerprint_data(request)

        if fingerprint_data is None:
            return

        fingerprint_service = DeviceFingerprintService(
            user=user,
            website=website,
        )

        fingerprint = fingerprint_service.create_or_update_fingerprint(
            fingerprint_data=fingerprint_data,
        )

        suspicious_findings = (
            fingerprint_service.find_suspicious_fingerprints(
                current_ip=fingerprint_data.get("ip_address"),
                current_user_agent=fingerprint_data.get("user_agent"),
                exclude_fingerprint_hash=fingerprint.fingerprint_hash,
            )
        )

        if suspicious_findings:
            DeviceSecurityAlertService.process_suspicious_fingerprints(
                user=user,
                website=website,
                suspicious_findings=suspicious_findings,
                ip_address=fingerprint_data.get("ip_address"),
            )

        DeviceSecurityAlertService.evaluate_and_alert_if_risky(
            user=user,
            website=website,
            fingerprint_service=fingerprint_service,
            fingerprint_hash=fingerprint.fingerprint_hash,
            ip_address=fingerprint_data.get("ip_address"),
            metadata={
                "user_agent": fingerprint_data.get("user_agent", ""),
            },
        )