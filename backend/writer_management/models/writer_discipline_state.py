"""
writer_management/models/writer_discipline_state.py

Cached summary of a writer's current discipline status.

SOURCE OF TRUTH vs CACHE
-------------------------
Source of truth:    WriterStrike, WriterWarning,
                    WriterSuspension, WriterBlacklist, WriterProbation

This model:         Fast-read cache rebuilt from source records
                    by WriterStatusService.recompute()

NEVER write to this model directly.
Always go through WriterStatusService.recompute() which reads
all source records and rebuilds this row atomically.

TWO SEPARATE COUNTERS
---------------------
Strikes and warnings are counted differently — intentionally.

    active_strike_count   = non-voided strikes (strikes never expire)
    lifetime_strike_count = all strikes ever (for blacklist threshold)

    active_warning_count  = non-voided, non-expired warnings
    lifetime_warning_count = all warnings ever

The eligibility check and escalation logic read these cached counts —
no per-request queries against the source tables.

ROUTING IMPACT
--------------
    is_suspended=True  → WriterCapacity.can_take_orders=False
    is_blacklisted=True → WriterCapacity.can_take_orders=False
    is_on_probation=True → NO routing impact (probation is a flag only)

Synced by WriterStatusService.recompute() after every update.
"""

from django.db import models
from django.utils.timezone import now


class WriterDisciplineState(models.Model):
    """
    Cached discipline summary for a writer.

    One row per writer. Created by signal on WriterProfile creation.
    Rebuilt by WriterStatusService.recompute() after every discipline event.
    """

    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="discipline_state",
    )

    # ----------------------------------------------------------------
    # SUSPENSION STATE
    # ----------------------------------------------------------------

    is_suspended = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "True when an active WriterSuspension exists. "
            "Rebuilt by WriterStatusService — never set directly."
        ),
    )
    suspension_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When the current suspension ends. "
            "Null if not suspended or suspension is indefinite."
        ),
    )

    # ----------------------------------------------------------------
    # BLACKLIST STATE
    # ----------------------------------------------------------------

    is_blacklisted = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "True when an active WriterBlacklist entry exists. "
            "Blacklist supersedes suspension. "
            "Rebuilt by WriterStatusService — never set directly."
        ),
    )

    # ----------------------------------------------------------------
    # PROBATION STATE
    # Does not affect routing — informational flag only.
    # ----------------------------------------------------------------

    is_on_probation = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "True when an active WriterProbation record exists. "
            "Does NOT block assignment routing. "
            "Rebuilt by WriterStatusService — never set directly."
        ),
    )
    probation_ends_at = models.DateTimeField(null=True, blank=True)

    # ----------------------------------------------------------------
    # STRIKE COUNTS
    # Strikes never expire — lifetime count is the same as active count
    # except for voided strikes which are excluded from active.
    # ----------------------------------------------------------------

    active_strike_count = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Non-voided strike count. "
            "Used for suspension threshold evaluation. "
            "Rebuilt by WriterStatusService."
        ),
    )
    lifetime_strike_count = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "All strikes ever issued including voided. "
            "Used for blacklist threshold evaluation "
            "(voided strikes still signal historical pattern)."
        ),
    )

    # ----------------------------------------------------------------
    # WARNING COUNTS
    # Warnings expire — active count excludes expired and voided.
    # ----------------------------------------------------------------

    active_warning_count = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Non-expired, non-voided warning count. "
            "Used for probation and suspension threshold evaluation. "
            "Rebuilt by WriterStatusService."
        ),
    )
    lifetime_warning_count = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "All warnings ever issued. "
            "Includes expired and voided warnings. "
            "Used for trend analysis — not threshold evaluation."
        ),
    )

    # ----------------------------------------------------------------
    # AUDIT
    # ----------------------------------------------------------------

    last_discipline_event_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Timestamp of the most recent discipline event "
            "(strike or warning). Used for admin dashboards."
        ),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this cache was last rebuilt.",
    )

    class Meta:
        verbose_name = "Writer Discipline State"
        verbose_name_plural = "Writer Discipline States"
        indexes = [
            # Bulk routing exclusion
            models.Index(
                fields=["is_suspended", "is_blacklisted"],
                name="discipline_routing_idx",
            ),
            # Admin dashboard: writers on probation
            models.Index(
                fields=["is_on_probation", "probation_ends_at"],
                name="discipline_probation_idx",
            ),
            # Admin dashboard: high warning count writers
            models.Index(
                fields=["active_warning_count"],
                name="discipline_warning_count_idx",
            ),
        ]
        constraints = [
            # Blacklist supersedes suspension — cannot be both
            models.CheckConstraint(
                condition=~(
                    models.Q(is_suspended=True) &
                    models.Q(is_blacklisted=True)
                ),
                name="discipline_not_suspended_and_blacklisted",
            ),
            # Counter sanity checks
            models.CheckConstraint(
                condition=models.Q(active_strike_count__gte=0),
                name="discipline_active_strikes_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(lifetime_strike_count__gte=0),
                name="discipline_lifetime_strikes_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    active_strike_count__lte=models.F("lifetime_strike_count")
                ),
                name="discipline_active_le_lifetime_strikes",
            ),
            models.CheckConstraint(
                condition=models.Q(active_warning_count__gte=0),
                name="discipline_active_warnings_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(lifetime_warning_count__gte=0),
                name="discipline_lifetime_warnings_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    active_warning_count__lte=models.F("lifetime_warning_count")
                ),
                name="discipline_active_le_lifetime_warnings",
            ),
            # Suspension timing: if not suspended, ends_at must be null
            models.CheckConstraint(
                condition=(
                    models.Q(is_suspended=True) |
                    models.Q(suspension_ends_at__isnull=True)
                ),
                name="discipline_suspension_ends_only_if_suspended",
            ),
        ]

    def __str__(self) -> str:
        flags = []
        if self.is_blacklisted:
            flags.append("blacklisted")
        elif self.is_suspended:
            flags.append("suspended")
        if self.is_on_probation:
            flags.append("probation")
        state = ", ".join(flags) if flags else "clean"
        return f"WriterDisciplineState<{self.writer.id}> [{state}]"

    # ----------------------------------------------------------------
    # CONVENIENCE PROPERTIES
    # Read only — never used for mutation decisions.
    # ----------------------------------------------------------------

    @property
    def is_restricted(self) -> bool:
        """True if writer is suspended or blacklisted."""
        return self.is_suspended or self.is_blacklisted

    @property
    def suspension_is_active(self) -> bool:
        """
        True if suspended and suspension has not timed out.
        WriterStatusService should have already cleared is_suspended
        when suspension_ends_at passes — this is a safety check.
        """
        if not self.is_suspended:
            return False
        if self.suspension_ends_at is None:
            return True
        return self.suspension_ends_at > now()

    @property
    def probation_is_active(self) -> bool:
        """True if on probation and probation has not timed out."""
        if not self.is_on_probation:
            return False
        if self.probation_ends_at is None:
            return True
        return self.probation_ends_at > now()

    @property
    def has_any_discipline_history(self) -> bool:
        """True if writer has ever received a warning or strike."""
        return self.lifetime_warning_count > 0 or self.lifetime_strike_count > 0