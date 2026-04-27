from __future__ import annotations

from django.db import models


class RolePermission(models.Model):
    """
    Links RoleDefinition to PermissionDefinition.
    """

    role = models.ForeignKey(
        "accounts.RoleDefinition",
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        "accounts.PermissionDefinition",
        on_delete=models.CASCADE,
        related_name="permission_roles",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self) -> str:
        return f"{self.role} -> {self.permission}"