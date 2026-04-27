from __future__ import annotations

from django.db import models


class PortalDefinition(models.Model):
    """
    Represents a login surface.

    Examples:
        internal_admin -> ordermanagement.com
        writer_portal -> writers.ordermanagement.com
        client_portal -> dynamic (gradecrest.com, etc)
    """

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=120)

    domain = models.CharField(
        max_length=255,
        help_text="Primary domain for this portal",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.code} ({self.domain})"