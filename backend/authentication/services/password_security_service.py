"""
Password security service.

Coordinate password validation, breach checking, password history,
expiration tracking, and password updates.
"""

import hashlib
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.password_security import PasswordBreachCheck
from authentication.services.password_history_service import (
    PasswordHistoryService,
)
from authentication.services.password_expiration_service import (
    PasswordExpirationService,
)
from authentication.services.password_breach_service import (
    PasswordBreachService,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.smart_password_policy import (
    SmartPasswordPolicy,
)


class PasswordSecurityService:
    """
    Orchestrate password security operations for a user on a website.

    This service is responsible for:
        - validating password quality and policy requirements
        - preventing recent password reuse
        - checking password breach exposure
        - updating password history
        - updating password expiration state
        - changing the user's password safely
        - revoking sessions when required
    """

    def __init__(self, user, website):
        """
        Initialize the password security service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for password security."
            )

        self.user = user
        self.website = website
        self.history_service = PasswordHistoryService(
            user=user,
            website=website,
        )
        self.expiration_service = PasswordExpirationService(
            user=user,
            website=website,
        )
        self.policy_service = SmartPasswordPolicy()

    def validate_new_password(
        self,
        *,
        raw_password: str,
        context: str = "password_change",
        check_history_depth: int | None = None,
        enforce_breach_check: bool = True,
    ) -> dict[str, Any]:
        """
        Validate a new password against policy, history, and breach
        rules.

        Args:
            raw_password: New plain-text password.
            context: Validation context.
            check_history_depth: Number of historical passwords to
                compare.
            enforce_breach_check: Whether to block breached passwords.

        Returns:
            Dictionary containing validation and breach-check results.

        Raises:
            ValidationError: If validation fails.
        """
        policy_result = self.policy_service.validate_password(
            password=raw_password,
            user=self.user,
            context=context,
            email=getattr(self.user, "email", None),
        )

        if not policy_result["valid"]:
            raise ValidationError(policy_result["errors"])

        self.history_service.validate_password_not_reused(
            raw_password=raw_password,
            check_last_n=check_history_depth,
        )

        breach_result = PasswordBreachService.check_password(raw_password)

        self._record_breach_check(
            password=raw_password,
            is_breached=bool(breach_result["is_breached"]),
            breach_count=int(breach_result["breach_count"]),
            action_taken=(
                PasswordBreachCheck.Action.FORCED_CHANGE
                if breach_result["is_breached"] and enforce_breach_check
                else PasswordBreachCheck.Action.NONE
            ),
        )

        if breach_result["is_breached"] and enforce_breach_check:
            raise ValidationError(
                f"This password has appeared in "
                f"{breach_result['breach_count']} known breach(es). "
                "Please choose a different password."
            )

        return {
            "policy": policy_result,
            "breach": breach_result,
        }

    @transaction.atomic
    def change_password(
        self,
        *,
        raw_password: str,
        context: str = "password_change",
        check_history_depth: int | None = None,
        revoke_other_sessions: bool = True,
        current_session_id: str | int | None = None,
        notify_user: bool = True,
    ) -> dict[str, Any]:
        """
        Validate and change the user's password securely.

        Args:
            raw_password: New plain-text password.
            context: Validation context.
            check_history_depth: Number of historical passwords to
                compare.
            revoke_other_sessions: Whether to revoke other active
                sessions after the password change.
            current_session_id: Optional current session ID to preserve.
            notify_user: Whether to send a password-changed
                notification.

        Returns:
            Dictionary describing the completed password update.

        Raises:
            ValidationError: If password validation fails.
        """
        validation_result = self.validate_new_password(
            raw_password=raw_password,
            context=context,
            check_history_depth=check_history_depth,
            enforce_breach_check=True,
        )

        self.history_service.save_current_password_to_history(
            history_depth=check_history_depth,
        )

        self.user.set_password(raw_password)
        self.user.save(update_fields=["password"])

        self.expiration_service.update_password_changed()

        revoked_sessions_count = 0
        if revoke_other_sessions:
            revoked_sessions_count = (
                LoginSessionService.revoke_all_sessions(
                    user=self.user,
                    website=self.website,
                    exclude_session_id=current_session_id,
                )
            )

        if notify_user:
            AuthNotificationBridgeService.send_password_changed_notification(
                user=self.user,
                website=self.website,
            )

        return {
            "changed": True,
            "revoked_sessions_count": revoked_sessions_count,
            "validation": validation_result,
        }

    def get_password_status(self) -> dict[str, Any]:
        """
        Return the current password-security status for the user.

        Returns:
            Dictionary containing expiration and history details.
        """
        expiration_status = self.expiration_service.get_expiration_status()

        return {
            "history_count": self.history_service.get_history_count(),
            "expiration": expiration_status,
            "password_change_required": (
                self.expiration_service.require_password_change()
            ),
            "warning_due": self.expiration_service.should_send_warning(),
        }

    def mark_expiration_warning_sent(self) -> None:
        """
        Mark that a password expiration warning was sent.
        """
        self.expiration_service.mark_warning_sent()

    def set_password_expiration_exemption(
        self,
        *,
        is_exempt: bool,
        reason: str = "",
    ) -> None:
        """
        Set password expiration exemption for the user.

        Args:
            is_exempt: Whether the user is exempt.
            reason: Optional audit reason.
        """
        self.expiration_service.set_exemption(
            is_exempt=is_exempt,
            reason=reason,
        )

    def update_password_expiration_policy(
        self,
        *,
        expires_in_days: int | None = None,
        warning_days_before: int | None = None,
    ) -> None:
        """
        Update password expiration policy settings.

        Args:
            expires_in_days: Password lifetime in days.
            warning_days_before: Warning lead time in days.
        """
        self.expiration_service.update_policy(
            expires_in_days=expires_in_days,
            warning_days_before=warning_days_before,
        )

    def _record_breach_check(
        self,
        *,
        password: str,
        is_breached: bool,
        breach_count: int,
        action_taken: str,
    ) -> PasswordBreachCheck:
        """
        Persist a password breach check result.

        Args:
            password: Plain-text password used for the check.
            is_breached: Whether password was found in breach data.
            breach_count: Number of breach appearances.
            action_taken: Action taken after the check.

        Returns:
            Created PasswordBreachCheck instance.
        """
        sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()
        prefix = sha1_hash[:5].upper()

        return PasswordBreachCheck.objects.create(
            user=self.user,
            website=self.website,
            password_hash_prefix=prefix,
            is_breached=is_breached,
            breach_count=breach_count,
            action_taken=action_taken,
        )