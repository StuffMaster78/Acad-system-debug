from __future__ import annotations

from django.conf import settings
from django.db import models

from class_management.constants import (
    ClassPortalActivityType,
    ClassPortalWorkLogVerificationStatus,
)


class ClassPortalWorkLog(models.Model):
    """
    Writer-reported record of work completed inside the school portal.

    Since actual class work happens outside our system, this model creates
    an internal progress trail for accountability, analytics, client updates,
    and admin review.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="portal_work_logs",
    )
    task = models.ForeignKey(
        "class_management.ClassTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portal_work_logs",
    )

    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="class_portal_work_logs",
    )

    activity_type = models.CharField(
        max_length=80,
        choices=ClassPortalActivityType.choices,
        db_index=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    portal_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Portal item title, module, week, quiz name, or reference.",
    )

    occurred_at = models.DateTimeField()
    logged_at = models.DateTimeField(auto_now_add=True)

    visible_to_client = models.BooleanField(default=True)

    verification_status = models.CharField(
        max_length=30,
        choices=ClassPortalWorkLogVerificationStatus.choices,
        default=ClassPortalWorkLogVerificationStatus.UNVERIFIED,
        db_index=True,
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_class_portal_work_logs",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    verification_notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-occurred_at", "-logged_at"]
        indexes = [
            models.Index(fields=["class_order", "activity_type"]),
            models.Index(fields=["writer", "logged_at"]),
            models.Index(fields=["verification_status"]),
            models.Index(fields=["visible_to_client"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} for class {self.class_order.pk}"