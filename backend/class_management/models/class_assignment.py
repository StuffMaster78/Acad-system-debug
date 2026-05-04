from __future__ import annotations

from django.conf import settings
from django.db import models

from class_management.constants import ClassAssignmentStatus


class ClassAssignment(models.Model):
    """
    Writer assignment history for a class order.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="class_assignments",
    )

    status = models.CharField(
        max_length=30,
        choices=ClassAssignmentStatus.choices,
        default=ClassAssignmentStatus.ACTIVE,
        db_index=True,
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_class_assignments",
    )

    assignment_notes = models.TextField(blank=True)
    removal_reason = models.TextField(blank=True)

    assigned_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assigned_at"]
        indexes = [
            models.Index(fields=["class_order", "status"]),
            models.Index(fields=["writer", "status"]),
        ]