from django.conf import settings
from django.db import models

class Reason(models.TextChoices):
    """Reason for Impersonating the user."""
    SUPPORT = "support", "Customer Support"
    DEBUG = "debug", "Debugging"
    FRAUD = "fraud", "Fraud Investigation"

class ImpersonationLog(models.Model):
    """
    Record impersonation actions for audit and accountability.
    """

    class Action(models.TextChoices):
        STARTED = "started", "Started"
        ENDED = "ended", "Ended"

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="impersonation_logs_as_admin",
        on_delete=models.CASCADE,
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="impersonation_logs_as_target",
        on_delete=models.CASCADE,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="impersonation_logs",
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )
    token = models.ForeignKey(
        "authentication.ImpersonationToken",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    reason = models.TextField(
        null=True,
        blank=True,
     )
    reason_type = models.CharField(choices=Reason.choices)
    reason_details = models.TextField()
    user_agent = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Impersonation Log"
        verbose_name_plural = "Impersonation Logs"
        indexes = [
            models.Index(fields=["admin_user", "website", "created_at"]),
            models.Index(fields=["target_user", "website", "created_at"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the impersonation log.
        """
        return (
            f"{self.admin_user} {self.action} impersonation of "
            f"{self.target_user} at {self.created_at:%Y-%m-%d %H:%M:%S}"
        )