"""
writer_management/models/writer_level_history.py

Append-only audit log of every level change for every writer.

REPLACES
--------
All 8 models from the old ranking.py:
    WriterAutoRanking
    WriterRankingHistory
    WriterRankingLog
    WriterRankingCriteria       → now WriterLevelCriteria
    WriterRankingCriteriaAdmin  → deleted (duplicate)
    WriterRanking               → live level is on WriterProfile.writer_level
    WriterRankingAdminReview    → admin_notes field on this model
    WriterRankingNotification   → platform notification system

ONE MODEL. ONE RESPONSIBILITY.
    Record that a level change happened, when, why, by what trigger,
    and what the before/after state was.

IMMUTABILITY
------------
Rows are never updated. Append only.
Do not add update_at or any mutable audit fields.
created_at is auto_now_add — set once, read forever.

LEVEL NAME SNAPSHOT
-------------------
previous_level_name and new_level_name capture the level name
by value at the time of the change. This preserves the audit trail
even if a WriterLevel row is later renamed or deactivated.
The FK fields (previous_level, new_level) use SET_NULL so the log
survives level deletion without cascading.

CREATION
--------
Only via:
    writer_management.services.level_progression_service
        .LevelProgressionService.record_change(...)

Never created directly. Never created in signals.
"""

from django.conf import settings
from django.db import models

from writer_management.enums import LevelChangeType, LevelChangeTrigger


class WriterLevelChangeLog(models.Model):
    """
    Immutable record of a single level change for a writer.

    Created by LevelProgressionService after every promotion,
    demotion, or manual override. Never updated.
    """

    # ----------------------------------------------------------------
    # WHO
    # ----------------------------------------------------------------

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="level_change_log",
        help_text="The writer whose level changed.",
    )

    # ----------------------------------------------------------------
    # WHAT — before and after
    # FKs use SET_NULL so log survives level deletion.
    # Name snapshots preserve audit trail if level is renamed.
    # ----------------------------------------------------------------

    previous_level = models.ForeignKey(
        "writer_management.WriterLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demoted_from_log",
        help_text="The level before the change. Null for initial assignment.",
    )
    previous_level_name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=(
            "Snapshot of WriterLevel.name at change time. "
            "Preserved even if the WriterLevel row is later renamed."
        ),
    )

    new_level = models.ForeignKey(
        "writer_management.WriterLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promoted_to_log",
        help_text="The level after the change.",
    )
    new_level_name = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Snapshot of the new WriterLevel.name at change time.",
    )

    # ----------------------------------------------------------------
    # WHY
    # ----------------------------------------------------------------

    change_type = models.CharField(
        max_length=20,
        choices=LevelChangeType.choices,
        help_text=(
            "Nature of the change: "
            "promotion / demotion / manual / initial."
        ),
    )

    triggered_by = models.CharField(
        max_length=20,
        choices=LevelChangeTrigger.choices,
        help_text=(
            "What caused the change: "
            "system (weekly task) / admin / onboarding."
        ),
    )

    reason = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Human-readable reason for the change. "
            "For system-triggered changes: the evaluation summary. "
            "For admin changes: admin's stated reason."
        ),
    )

    admin_notes = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Additional notes from admin review. "
            "Only populated for manual overrides."
        ),
    )

    # ----------------------------------------------------------------
    # WHO TRIGGERED IT
    # ----------------------------------------------------------------

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_level_changes",
        help_text=(
            "The admin user who made the change. "
            "Null for system-triggered changes."
        ),
    )

    # ----------------------------------------------------------------
    # PERFORMANCE CONTEXT SNAPSHOT
    # What the writer's key metrics were at the time of the change.
    # Stored as a JSON snapshot so the audit log is self-contained.
    # ----------------------------------------------------------------

    performance_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Key performance metrics at time of evaluation. "
            "Schema: { "
            "'composite_score': float, "
            "'avg_rating': float, "
            "'completion_rate': float, "
            "'revision_rate': float, "
            "'lateness_rate': float, "
            "'dispute_rate': float, "
            "'period_start': 'YYYY-MM-DD', "
            "'period_end': 'YYYY-MM-DD' "
            "}"
        ),
    )

    # ----------------------------------------------------------------
    # WHEN — immutable
    # ----------------------------------------------------------------

    changed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Writer Level Change Log"
        verbose_name_plural = "Writer Level Change Log"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(
                fields=["writer", "changed_at"],
                name="level_change_writer_time_idx",
            ),
            models.Index(
                fields=["change_type", "changed_at"],
                name="level_change_type_time_idx",
            ),
            models.Index(
                fields=["triggered_by", "changed_at"],
                name="level_change_trigger_time_idx",
            ),
        ]
        # No update constraints needed — this model is append-only.
        # Immutability is enforced by service contract, not DB constraint.

    def __str__(self) -> str:
        return (
            f"LevelChange<{self.writer.id}> "
            f"{self.previous_level_name or 'none'} → "
            f"{self.new_level_name} "
            f"[{self.change_type}] @ {self.changed_at:%Y-%m-%d}"
        )