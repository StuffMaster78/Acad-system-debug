from django.db import models


class RetentionScope(models.TextChoices):
    GLOBAL = "global", "Global"
    WEBSITE = "website", "Website"
    ACTION = "action", "Action"


class AuditRetentionPolicy(models.Model):
    """
    Defines how long audit logs live.
    """

    scope = models.CharField(
        max_length=20,
        choices=RetentionScope.choices,
        db_index=True,
    )

    website_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    action_prefix = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Example: billing., order., auth.",
    )

    retention_days = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)