from django.conf import settings
from django.db import models

from accounts.enums import AccountAuditEventType


class AccountAuditLog(models.Model):
    """Stores audit events for account lifecycle activity."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_audit_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_audit_logs",
    )
    account_profile = models.ForeignKey(
        "accounts.AccountProfile",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    event_type = models.CharField(
        max_length=60,
        choices=AccountAuditEventType.choices,
    )
    description = models.TextField(blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_audit_events_triggered",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_account_audit_log"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable representation of the audit log."""
        return f"{self.event_type} for {self.user}"