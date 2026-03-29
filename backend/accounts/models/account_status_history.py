from django.conf import settings
from django.db import models

from accounts.enums import AccountStatus


class AccountStatusHistory(models.Model):
    """Tracks status transitions for account profiles."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_status_history",
    )
    account_profile = models.ForeignKey(
        "accounts.AccountProfile",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    old_status = models.CharField(
        max_length=30,
        choices=AccountStatus.choices,
    )
    new_status = models.CharField(
        max_length=30,
        choices=AccountStatus.choices,
    )
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="changed_account_statuses",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_account_status_history"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable representation of the status history row."""
        return (
            f"{self.account_profile} {self.old_status} -> {self.new_status}"
        )