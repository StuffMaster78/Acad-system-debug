from django.db import models


class ConfigScope(models.TextChoices):
    GLOBAL = "global", "Global"
    WEBSITE = "website", "Website"
    USER = "user", "User"


class ConfigItem(models.Model):
    key = models.CharField(
        max_length=255,
        db_index=True,
    )

    value = models.JSONField()

    scope = models.CharField(
        max_length=20,
        choices=ConfigScope.choices,
        default=ConfigScope.GLOBAL,
        db_index=True,
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configs",
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="configs",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_configs",
    )

    class Meta:
        indexes = [
            models.Index(fields=["key", "scope"]),
            models.Index(fields=["website"]),
            models.Index(fields=["is_active"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["key", "scope", "website", "user"],
                name="unique_config_scope_target",
            )
        ]

    def __str__(self):
        return f"{self.key} ({self.scope})"