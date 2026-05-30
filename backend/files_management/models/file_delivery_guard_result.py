from __future__ import annotations

from django.conf import settings
from django.db import models

from files_management.enums import DeliveryGuardBlockReason


class FileDeliveryGuardResult(models.Model):
    """
    Records the outcome of a delivery guard check for a file attachment.

    A guard check decides whether a client is allowed to download a final
    or milestone file. Results are stored so the UI can display the correct
    locked state and so ops can audit access decisions.

    One attachment may accumulate many results as the guard is re-evaluated
    over time (e.g. partial payment → full payment → unlocked).
    """

    RESULT_ALLOWED = "allowed"
    RESULT_BLOCKED = "blocked"
    RESULT_CHOICES = [
        (RESULT_ALLOWED, "Allowed"),
        (RESULT_BLOCKED, "Blocked"),
    ]

    attachment = models.ForeignKey(
        "files_management.FileAttachment",
        on_delete=models.CASCADE,
        related_name="delivery_guard_results",
    )

    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="delivery_guard_checks",
        help_text="User who triggered the guard check. Null for system checks.",
    )

    result = models.CharField(
        max_length=16,
        choices=RESULT_CHOICES,
        db_index=True,
    )

    blocked_reason = models.CharField(
        max_length=32,
        choices=DeliveryGuardBlockReason.choices,
        blank=True,
        help_text="Populated only when result is blocked.",
    )

    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Outstanding balance at the time of check, for display.",
    )

    checked_at = models.DateTimeField(auto_now_add=True, db_index=True)

    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set when the guard first returns ALLOWED for this attachment.",
    )

    class Meta:
        ordering = ["-checked_at"]
        indexes = [
            models.Index(fields=["attachment", "result"]),
            models.Index(fields=["attachment", "checked_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"Guard {self.result} for attachment {self.attachment_id} "
            f"at {self.checked_at}"
        )

    @property
    def is_allowed(self) -> bool:
        return self.result == self.RESULT_ALLOWED

    @property
    def is_blocked(self) -> bool:
        return self.result == self.RESULT_BLOCKED
