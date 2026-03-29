from django.conf import settings
from django.db import models


class AccountRole(models.Model):
    """Assigns a role definition to an account profile."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_roles",
    )
    account_profile = models.ForeignKey(
        "accounts.AccountProfile",
        on_delete=models.CASCADE,
        related_name="roles",
    )
    role = models.ForeignKey(
        "accounts.RoleDefinition",
        on_delete=models.PROTECT,
        related_name="account_roles",
    )
    is_active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_account_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "accounts_account_role"
        constraints = [
            models.UniqueConstraint(
                fields=["account_profile", "role"],
                name="unique_role_per_account_profile",
            ),
        ]
        ordering = ["role__name", "-assigned_at"]

    def __str__(self) -> str:
        """Return a readable representation of the role assignment."""
        return f"{self.account_profile} -> {self.role.key}"