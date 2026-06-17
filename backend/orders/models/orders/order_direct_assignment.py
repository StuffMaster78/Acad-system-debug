from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from websites.models.websites import Website


class OrderDirectAssignment(models.Model):
    """
    Tracks the writer acceptance gate for staff-direct assignments.

    Created when staff calls assign_directly; the order stays in
    pending_writer_acceptance until the writer accepts or rejects.
    """

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_direct_assignments",
    )
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="direct_assignment",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="direct_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_assignments_made",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    reason = models.TextField(blank=True, default="")
    assigned_at = models.DateTimeField(default=timezone.now)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self) -> str:
        return (
            f"DirectAssignment order={self.order_id} "
            f"writer={self.writer_id} [{self.status}]"
        )
