from __future__ import annotations

from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    `created_at` and `updated_at` fields.

    Design goals:
        - Consistent audit fields across all models
        - Pylance-friendly typing
        - No business logic
        - Safe for multi-tenant usage
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """
        Default string representation.
        Override in child models when needed.
        """
        return f"{self.__class__.__name__}(id={getattr(self, 'id', None)})"