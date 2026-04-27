from __future__ import annotations

from django.conf import settings
from django.db import models


class PortalAccess(models.Model):
    """
    Grants a user access to a portal.

    Example:
        user -> internal_admin
        user -> writer_portal
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portal_accesses",
    )
    portal = models.ForeignKey(
        "accounts.PortalDefinition",
        on_delete=models.PROTECT,
        related_name="user_accesses",
    )

    is_active = models.BooleanField(default=True)

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_portal_accesses",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "portal")

    def __str__(self) -> str:
        return f"{self.user} -> {self.portal}"