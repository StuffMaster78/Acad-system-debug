from __future__ import annotations

from django.db import models


class PermissionDefinition(models.Model):
    """
    Defines a single permission in the system.

    Example:
        orders.view_all
        orders.assign_writer
        payments.refund
    """

    code = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code