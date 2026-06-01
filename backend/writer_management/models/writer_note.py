"""
Internal administrative notes about writers.

Private operational notes visible only to staff and admins.
Writers never see these.

Used for:
    - Behavioral observations during order monitoring
    - Internal warnings before formal discipline
    - Quality concerns not yet escalating to a strike/warning
    - Escalation context ("this writer has been difficult with clients")
    - Onboarding assessment notes
    - Positive observations ("consistently high quality, consider fast-tracking")

These are NOT discipline records. They carry no formal weight,
trigger no automated actions, and have no threshold logic.
They are human notes for human admins.

If a note leads to a formal action, use DisciplineService.
The note remains as context for why that action was taken.
"""

from django.conf import settings
from django.db import models


class WriterNote(models.Model):
    """
    Internal admin note attached to a writer.

    Append-friendly — notes are rarely edited after creation.
    Pinned notes appear at the top of the writer's note history.
    Sensitive notes may require elevated admin permissions to view.

    Created by: Admin via admin API
    Visible to: Staff and admins only — never to writers
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_notes",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="notes",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="writer_notes_created",
        help_text="Admin who wrote the note.",
    )

    note = models.TextField(
        help_text=(
            "Internal note content. "
            "Be factual and specific. "
            "These notes may be reviewed in dispute or legal proceedings."
        ),
    )

    is_pinned = models.BooleanField(
        default=False,
        help_text=(
            "Pinned notes appear first in the writer's note history. "
            "Use for critical ongoing concerns."
        ),
    )

    is_sensitive = models.BooleanField(
        default=False,
        help_text=(
            "Sensitive notes contain information requiring elevated "
            "admin permissions to view (e.g. fraud investigation details, "
            "legal hold notices)."
        ),
    )

    # Optional link to a specific order for context
    related_order_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional order PK this note relates to.",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Note"
        verbose_name_plural = "Writer Notes"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(
                fields=["writer", "is_pinned", "created_at"],
                name="writer_note_writer_pin_idx",
            ),
            models.Index(
                fields=["website", "created_at"],
                name="writer_note_site_time_idx",
            ),
        ]

    def __str__(self) -> str:
        pinned = " [pinned]" if self.is_pinned else ""
        sensitive = " [sensitive]" if self.is_sensitive else ""
        return (
            f"WriterNote<{self.writer.id}>"
            f"{pinned}{sensitive} "
            f"@ {self.created_at:%Y-%m-%d}"
        )