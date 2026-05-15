"""
Pen name change request workflow.

Writers cannot change their pen_name directly via the profile API.
They must submit a WriterPenNameChangeRequest which an admin approves.
On approval, pen_name_service updates WriterProfile.pen_name.

This keeps pen_name auditable — every change has a request record.
"""

from django.conf import settings
from django.db import models
from writer_management.enums import WriterPenNameStatus

class WriterPenNameChangeRequest(models.Model):
    """
    A request by a writer to change their display pen name.

    Workflow:
        1. Writer submits request with requested_name and reason.
        2. Admin reviews — approves or rejects.
        3. On approval, pen_name_service updates WriterProfile.pen_name
           and records the change.

    One pending request per writer at a time enforced by
    partial UniqueConstraint.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="pen_name_requests",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="pen_name_requests",
    )

    current_name = models.CharField(
        max_length=100,
        help_text="Pen name at time of request. Snapshot for audit.",
    )
    requested_name = models.CharField(
        max_length=100,
        help_text="The pen name the writer wants to use.",
    )
    reason = models.TextField(
        help_text="Why the writer wants to change their pen name.",
    )

    status = models.CharField(
        max_length=20,
        choices=WriterPenNameStatus.choices,
        default=WriterPenNameStatus.PENDING,
        db_index=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pen_name_reviews",
    )
    review_notes = models.TextField(blank=True, default="")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Pen Name Change Request"
        verbose_name_plural = "Writer Pen Name Change Requests"
        ordering = ["-requested_at"]
        constraints = [
            # Only one pending request per writer at a time
            models.UniqueConstraint(
                fields=["writer"],
                condition=models.Q(status="pending"),
                name="unique_pending_pen_name_request",
            ),
            # Review fields must be set together
            models.CheckConstraint(
                condition=(
                    models.Q(reviewed_by__isnull=True) |
                    models.Q(reviewed_at__isnull=False)
                ),
                name="pen_name_review_has_timestamp",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"PenNameRequest<{self.writer.id}> "
            f"'{self.requested_name}' [{self.status}]"
        )