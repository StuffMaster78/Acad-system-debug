from django.db import models


class RoleDefinition(models.Model):
    """Defines a role that can be assigned to account profiles."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="role_definitions",
    )
    key = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_role_definition"
        constraints = [
            models.UniqueConstraint(
                fields=["website", "key"],
                name="unique_role_definition_per_website_key",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        """Return a readable representation of the role definition."""
        return f"{self.name} ({self.key})"