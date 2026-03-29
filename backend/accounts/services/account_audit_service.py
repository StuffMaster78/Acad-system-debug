from typing import Any

from accounts.models import AccountAuditLog, AccountProfile


class AccountAuditService:
    """Service for creating account audit log entries."""

    @staticmethod
    def log_event(
        *,
        account_profile: AccountProfile,
        event_type: str,
        description: str = "",
        actor=None,
        metadata: dict[str, Any] | None = None,
    ) -> AccountAuditLog:
        """Create an audit log entry for an account profile."""
        return AccountAuditLog.objects.create(
            website=account_profile.website,
            user=account_profile.user,
            account_profile=account_profile,
            event_type=event_type,
            description=description,
            actor=actor,
            metadata=metadata or {},
        )