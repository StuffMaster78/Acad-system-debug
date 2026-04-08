"""
Production-grade impersonation service.

This service handles secure impersonation workflows with:
    - strong permission checks
    - hashed impersonation tokens
    - session-based impersonation state
    - JWT impersonation claims
    - audit logging
    - safe start and end flows

Notes:
    - Raw impersonation tokens must never be stored in the database.
    - Models should remain state-focused. Workflow lives here.
    - Impersonation is security-sensitive and should always be audited.
"""

import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models.impersonation_log import (
    ImpersonationLog
)
from authentication.models.impersonation_token import (
    ImpersonationToken,
)
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)
from authentication.services.token_service import TokenService
from authentication.utils.ip import get_client_ip
from websites.utils import get_current_website


logger = logging.getLogger(__name__)
User = get_user_model()


class ImpersonationService:
    """
    Handle impersonation token creation, impersonation start,
    impersonation end, and impersonation state inspection.

    This service is responsible for:
        - validating impersonation permissions
        - issuing impersonation tokens
        - consuming impersonation tokens
        - starting impersonation sessions
        - ending impersonation sessions
        - generating JWTs for impersonated and original users
        - writing impersonation audit logs
    """

    SESSION_FLAG = "is_impersonating"
    SESSION_ADMIN_USER_ID = "impersonator_user_id"
    SESSION_ADMIN_EMAIL = "impersonator_email"
    SESSION_ADMIN_ROLE = "impersonator_role"
    SESSION_TARGET_USER_ID = "impersonated_user_id"
    SESSION_STARTED_AT = "impersonation_started_at"

    DEFAULT_EXPIRY_HOURS = 1

    def __init__(self, request, website=None):
        """
        Initialize the impersonation service.

        Args:
            request: HTTP request object.
            website: Optional website instance. If omitted, it will be
                resolved from the request.

        Raises:
            ValueError: If website context cannot be resolved.
        """
        self.request = request
        self.website = website or get_current_website(request)
        self.admin_user = (
            request.user
            if getattr(request.user, "is_authenticated", False)
            else None
        )

        if not self.website:
            raise ValueError(
                "Website context is required for impersonation."
            )

    @staticmethod
    def _get_user_agent(request) -> str:
        """
        Extract the user agent string from the request.

        Args:
            request: HTTP request object.

        Returns:
            User agent string, or an empty string if unavailable.
        """
        if request is None:
            return ""

        return request.headers.get("User-Agent", "")

    @staticmethod
    def can_impersonate(admin_user, target_user) -> tuple[bool, str]:
        """
        Determine whether an admin user may impersonate a target user.

        Args:
            admin_user: User attempting impersonation.
            target_user: User to be impersonated.

        Returns:
            A tuple of:
                - whether impersonation is allowed
                - denial reason if not allowed
        """
        if not admin_user or not admin_user.is_authenticated:
            return False, "Admin user must be authenticated."

        if not getattr(admin_user, "is_staff", False):
            return False, "Only staff members can impersonate users."

        if admin_user.pk == target_user.pk:
            return False, "You cannot impersonate yourself."

        if not getattr(target_user, "is_active", False):
            return False, "Cannot impersonate an inactive user."

        admin_role = getattr(admin_user, "role", None)
        target_role = getattr(target_user, "role", None)

        if admin_role == "superadmin":
            return True, ""

        if admin_role == "admin":
            if target_role in {"client", "writer"}:
                return True, ""
            return (
                False,
                "Admins can only impersonate clients and writers.",
            )

        return False, "Insufficient permissions for impersonation."

    @classmethod
    @transaction.atomic
    def create_token(
        cls,
        *,
        admin_user,
        target_user,
        website,
        expires_hours: int = DEFAULT_EXPIRY_HOURS,
        reason: str = "",
    ) -> tuple[ImpersonationToken, str]:
        """
        Create a new impersonation token.

        Args:
            admin_user: Authorized admin initiating impersonation.
            target_user: User to be impersonated.
            website: Website or tenant context.
            expires_hours: Token lifetime in hours.

        Returns:
            A tuple of:
                - created ImpersonationToken instance
                - raw impersonation token

        Raises:
            PermissionDenied: If impersonation is not allowed.
            ValidationError: If token expiry is invalid.
        """
        allowed, denial_reason = cls.can_impersonate(
            admin_user=admin_user,
            target_user=target_user,
        )
        AccountAccessPolicyService.validate_auth_access(
            user=target_user,
            website=website,

        )
        if not allowed:
            raise PermissionDenied(denial_reason)
        
        if not reason:
            raise ValidationError(
                "Reason is required for impersonation."
            )

        if expires_hours <= 0:
            raise ValidationError(
                "Token expiry must be greater than zero."
            )

        raw_token, token_hash = TokenService.generate_hashed_token()

        token = ImpersonationToken.objects.create(
            admin_user=admin_user,
            target_user=target_user,
            website=website,
            token_hash=token_hash,
            expires_at=TokenService.build_expiry(
                hours=expires_hours,
            ),
        )

        logger.info(
            "Admin %s generated impersonation token for user %s "
            "on website %s",
            admin_user.pk,
            target_user.pk,
            getattr(website, "pk", None),
        )

        return token, raw_token

    @transaction.atomic
    def start_impersonation(
        self,
        *,
        raw_token: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Start impersonation using a valid impersonation token.

        Args:
            raw_token: Raw impersonation token string.

        Returns:
            A dictionary containing JWT tokens, impersonated user info,
            and impersonation metadata.

        Raises:
            PermissionDenied: If the token is invalid or unauthorized.
        """
        token_hash = TokenService.hash_value(raw_token)
        website = self.website
        if website is None:
            raise PermissionDenied("Website context is required.") 

        try:
            token = ImpersonationToken.objects.select_related(
                "admin_user",
                "target_user",
                "website",
            ).get(
                token_hash=token_hash,
                website=website,
                used_at__isnull=True,
            )
            
        except ImpersonationToken.DoesNotExist as exc:
            raise PermissionDenied(
                "Invalid impersonation token."
            ) from exc

        
        if not token.is_valid:
            raise PermissionDenied(
                "Impersonation token is invalid or expired."
            )

        if token.website.pk != website.pk:
            raise PermissionDenied("Cross-tenant impersonation denied.")
        
        if not self.admin_user or token.admin_user.pk != self.admin_user.pk:
            raise PermissionDenied(
                "You are not authorized to use this impersonation token."
            )
        
        if self.is_impersonating():
            raise PermissionDenied(
                "Already impersonating a user. End current session first."
            )

        allowed, denial_reason = self.can_impersonate(
            admin_user=self.admin_user,
            target_user=token.target_user,
        )
        if not allowed:
            raise PermissionDenied(denial_reason)

        AccountAccessPolicyService.validate_auth_access(
            user=token.target_user,
            website=website,

        )

        if hasattr(self.request, "session"):
            self.request.session.cycle_key()
            self.request.session[self.SESSION_FLAG] = True
            self.request.session[self.SESSION_ADMIN_USER_ID] = (
                self.admin_user.pk
            )
            self.request.session[self.SESSION_ADMIN_EMAIL] = (
                getattr(self.admin_user, "email", "")
            )
            self.request.session[self.SESSION_ADMIN_ROLE] = (
                getattr(self.admin_user, "role", None)
            )
            self.request.session[self.SESSION_TARGET_USER_ID] = (
                token.target_user.pk
            )
            self.request.session[self.SESSION_STARTED_AT] = (
                timezone.now().isoformat()
            )
            self.request.session["_auth_user_id"] = str(
                token.target_user.pk
            )
            self.request.session.save()

        token.mark_as_used()

        ImpersonationLog.objects.create(
            admin_user=self.admin_user,
            target_user=token.target_user,
            website=self.website,
            action=ImpersonationLog.Action.STARTED,
            token=token,
            ip_address=get_client_ip(self.request),
            user_agent=self._get_user_agent(self.request),
            reason=reason or "Impersonation Started. No reason provided.",
        )

        refresh = RefreshToken.for_user(token.target_user)
        refresh["impersonated_by"] = self.admin_user.pk
        refresh["is_impersonation"] = True
        refresh["website_id"] = getattr(self.website, "pk", None)
        refresh["session_id"] = self.session.pk

        logger.info(
            "Admin %s started impersonating user %s on website %s",
            self.admin_user.pk,
            token.target_user.pk,
            getattr(self.website, "pk", None),
        )

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": token.target_user.pk,
                "email": getattr(token.target_user, "email", ""),
                "username": getattr(token.target_user, "username", ""),
                "full_name": (
                    token.target_user.get_full_name()
                    if hasattr(token.target_user, "get_full_name")
                    else ""
                ),
                "role": getattr(token.target_user, "role", None),
            },
            "impersonation": {
                "is_impersonation": True,
                "impersonated_by": {
                    "id": self.admin_user.pk,
                    "email": getattr(self.admin_user, "email", ""),
                    "full_name": (
                        self.admin_user.get_full_name()
                        if hasattr(self.admin_user, "get_full_name")
                        else ""
                    ),
                    "role": getattr(self.admin_user, "role", None),
                },
                "started_at": timezone.now().isoformat(),
            },
            "expires_in": 3600,
        }

    @transaction.atomic
    def end_impersonation(
        self,
        *,
        close_tab: bool = False,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """
        End an active impersonation session and restore the original
        admin context.

        Args:
            close_tab: Whether this end action comes from an
                impersonation tab that will be closed.

        Returns:
            A dictionary containing either:
                - confirmation only, if close_tab=True
                - fresh JWT tokens for the original admin, if
                  close_tab=False

        Raises:
            PermissionDenied: If no impersonation is active.
        """
        impersonator_id = None

        if hasattr(self.request, "session"):
            impersonator_id = self.request.session.get(
                self.SESSION_ADMIN_USER_ID,
            )

        if not impersonator_id and hasattr(self.request, "auth"):
            try:
                impersonator_id = self.request.auth.get(
                    "impersonated_by",
                )
            except (AttributeError, TypeError):
                impersonator_id = None

        if not impersonator_id:
            raise PermissionDenied(
                "No impersonation session found."
            )

        try:
            original_admin = User.objects.get(pk=impersonator_id)
        except User.DoesNotExist as exc:
            raise PermissionDenied(
                "Original admin user not found."
            ) from exc

        target_user_id = None

        if hasattr(self.request, "session"):
            target_user_id = self.request.session.get(
                self.SESSION_TARGET_USER_ID,
            )

        if not target_user_id:
            raise PermissionDenied(
                "No impersonated user context found."
            )

        try:
            current_user = User.objects.get(pk=target_user_id)
        except User.DoesNotExist as exc:
            raise PermissionDenied(
                "Impersonated user not found."
            ) from exc

        ImpersonationLog.objects.create(
            admin_user=original_admin,
            target_user=current_user,
            website=self.website,
            action=ImpersonationLog.Action.ENDED,
            token=None,
            ip_address=get_client_ip(self.request),
            user_agent=self._get_user_agent(self.request),
            reason=reason or "Impersonation session ended.",
        )

        if hasattr(self.request, "session"):
            self.request.session.cycle_key()
            self.request.session["_auth_user_id"] = str(
                original_admin.pk
            )
            self.request.session.pop(self.SESSION_FLAG, None)
            self.request.session.pop(self.SESSION_ADMIN_USER_ID, None)
            self.request.session.pop(self.SESSION_ADMIN_EMAIL, None)
            self.request.session.pop(self.SESSION_ADMIN_ROLE, None)
            self.request.session.pop(self.SESSION_TARGET_USER_ID, None)
            self.request.session.pop(self.SESSION_STARTED_AT, None)
            self.request.session.save()

        logger.info(
            "Admin %s ended impersonation of user %s on website %s "
            "(close_tab=%s)",
            original_admin.pk,
            current_user.pk,
            getattr(self.website, "pk", None),
            close_tab,
        )

        if close_tab:
            return {
                "message": "Impersonation ended. Tab will close.",
                "close_tab": True,
                "user": {
                    "id": original_admin.pk,
                    "email": getattr(original_admin, "email", ""),
                    "username": getattr(original_admin, "username", ""),
                    "full_name": (
                        original_admin.get_full_name()
                        if hasattr(original_admin, "get_full_name")
                        else ""
                    ),
                    "role": getattr(original_admin, "role", None),
                },
            }

        refresh = RefreshToken.for_user(original_admin)
        refresh["website_id"] = getattr(self.website, "pk", None)

        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": original_admin.pk,
                "email": getattr(original_admin, "email", ""),
                "username": getattr(original_admin, "username", ""),
                "full_name": (
                    original_admin.get_full_name()
                    if hasattr(original_admin, "get_full_name")
                    else ""
                ),
                "role": getattr(original_admin, "role", None),
            },
            "message": (
                "Impersonation ended. You are now logged in as yourself."
            ),
            "close_tab": False,
        }

    def is_impersonating(self) -> bool:
        """
        Determine whether the current request is in an active
        impersonation context.

        Returns:
            True if impersonation is active, otherwise False.
        """
        if hasattr(self.request, "session"):
            if self.request.session.get(self.SESSION_FLAG):
                return True

        if hasattr(self.request, "auth"):
            try:
                return bool(
                    self.request.auth.get("is_impersonation", False)
                )
            except (AttributeError, TypeError):
                return False

        return False

    def get_impersonator_info(self) -> dict[str, Any] | None:
        """
        Retrieve information about the current impersonator.

        Returns:
            A dictionary containing impersonator metadata, or None if
            impersonation is not active.
        """
        if not self.is_impersonating():
            return None

        impersonator_id = None

        if hasattr(self.request, "session"):
            impersonator_id = self.request.session.get(
                self.SESSION_ADMIN_USER_ID,
            )

        if not impersonator_id and hasattr(self.request, "auth"):
            try:
                impersonator_id = self.request.auth.get(
                    "impersonated_by",
                )
            except (AttributeError, TypeError):
                impersonator_id = None

        if not impersonator_id:
            return None

        try:
            admin_user = User.objects.get(pk=impersonator_id)
        except User.DoesNotExist:
            return None

        return {
            "id": admin_user.pk,
            "email": getattr(admin_user, "email", ""),
            "full_name": (
                admin_user.get_full_name()
                if hasattr(admin_user, "get_full_name")
                else ""
            ),
            "role": getattr(admin_user, "role", None),
        }
    
    @staticmethod
    def cleanup_expired_tokens() -> int:
        """
        Delete expired impersonation tokens.

        Returns:
            Number of deleted token records.
        """
        deleted_count, _ = ImpersonationToken.objects.filter(
            expires_at__lt=timezone.now(),
        ).delete()

        return deleted_count