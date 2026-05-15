"""
writer_management/models/writer_status.py

Real-time online presence for a writer.

Answers: "Is this writer at their keyboard right now?"

WHAT THIS IS NOT
----------------
This is NOT assignment eligibility.
This is NOT discipline state.
This is NOT availability.

An OFFLINE writer is still eligible for assignment routing.
Online status is presence information only — shown in dashboards,
used for auto-offline logic, visible to admins.

WHAT THIS IS
------------
A single high-churn row per writer that tracks:
    - Current presence state (ONLINE / OFFLINE / AWAY / BUSY)
    - Optional status message ("Back in 30 mins")
    - When the status last changed
    - When the writer was last seen

CHURN PROFILE
-------------
High write frequency. Updated:
    - On every heartbeat ping (WebSocket or polling)
    - On login / logout
    - By the auto-offline Celery task every 5 minutes

Keep this row on a separate table from WriterProfile to avoid
lock contention during heartbeat updates.

MUTATION
--------
Only via mark_online() and mark_offline() methods.
Never set status field directly — the methods guard against
no-op writes (same state → no DB write).
"""

from django.db import models
from django.utils.timezone import now

from writer_management.enums import WriterOnlineStatus


class WriterStatus(models.Model):
    """
    Runtime online presence for a writer.

    One row per writer. Created by signal on WriterProfile creation.
    """

    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="status",
    )

    status = models.CharField(
        max_length=20,
        choices=WriterOnlineStatus.choices,
        default=WriterOnlineStatus.OFFLINE,
        db_index=True,
    )

    status_message = models.CharField(
        max_length=160,
        blank=True,
        default="",
        help_text=(
            "Optional short message set by the writer. "
            "e.g. 'Back in 30 mins'. "
            "Cleared automatically on logout."
        ),
    )

    last_changed_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        help_text="When the status last changed. Auto-updated on every save.",
    )

    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "Last confirmed presence timestamp. "
            "Updated on every heartbeat ping. "
            "Used by auto-offline task to determine inactivity."
        ),
    )

    class Meta:
        verbose_name = "Writer Status"
        verbose_name_plural = "Writer Statuses"
        indexes = [
            models.Index(
                fields=["status", "last_seen_at"],
                name="writer_status_presence_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"WriterStatus<{self.writer.id}> [{self.status}]"

    # ----------------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------------

    @property
    def is_online(self) -> bool:
        return self.status == WriterOnlineStatus.ONLINE

    @property
    def is_offline(self) -> bool:
        return self.status == WriterOnlineStatus.OFFLINE

    @property
    def is_away(self) -> bool:
        return self.status == WriterOnlineStatus.AWAY

    @property
    def is_busy(self) -> bool:
        return self.status == WriterOnlineStatus.BUSY

    # ----------------------------------------------------------------
    # MUTATIONS
    # Always go through these methods — never set status directly.
    # Guard against no-op writes (same state = no DB hit).
    # ----------------------------------------------------------------

    def mark_online(self, message: str = "") -> None:
        """
        Set status to ONLINE and record last_seen_at.
        No-op if already ONLINE with the same message.
        """
        n = now()
        changed = (
            self.status != WriterOnlineStatus.ONLINE or
            self.status_message != message
        )
        self.last_seen_at = n
        if changed:
            self.status = WriterOnlineStatus.ONLINE
            self.status_message = message
            self.save(update_fields=["status", "status_message",
                                     "last_seen_at", "last_changed_at"])
        else:
            # Still update last_seen_at on every heartbeat
            self.save(update_fields=["last_seen_at"])

    def mark_offline(self, message: str = "") -> None:
        """
        Set status to OFFLINE. Clears message unless one is provided.
        No-op if already OFFLINE.
        """
        if self.status == WriterOnlineStatus.OFFLINE:
            return
        self.status = WriterOnlineStatus.OFFLINE
        self.status_message = message
        self.save(update_fields=["status", "status_message", "last_changed_at"])

    def mark_away(self, message: str = "") -> None:
        """Set status to AWAY with optional message."""
        if (self.status == WriterOnlineStatus.AWAY and
                self.status_message == message):
            return
        self.status = WriterOnlineStatus.AWAY
        self.status_message = message
        self.save(update_fields=["status", "status_message", "last_changed_at"])

    def mark_busy(self, message: str = "") -> None:
        """Set status to BUSY with optional message."""
        if (self.status == WriterOnlineStatus.BUSY and
                self.status_message == message):
            return
        self.status = WriterOnlineStatus.BUSY
        self.status_message = message
        self.save(update_fields=["status", "status_message", "last_changed_at"])

    def record_heartbeat(self) -> None:
        """
        Record that the writer is still present without changing status.
        Called on every WebSocket ping or API activity.
        Only updates last_seen_at — cheapest possible write.
        """
        self.last_seen_at = now()
        self.save(update_fields=["last_seen_at"])