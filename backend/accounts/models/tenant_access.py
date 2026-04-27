from __future__ import annotations

from django.conf import settings
from django.db import models


class TenantAccess(models.Model):
    """
    Grants a user access to a website (tenant).

    Example:
        user -> Gradecrest
        user -> NurseMyGrade
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_accesses",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="user_accesses",
    )

    is_active = models.BooleanField(default=True)

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_tenant_accesses",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "website")

    def __str__(self) -> str:
        return f"{self.user} -> {self.website}"