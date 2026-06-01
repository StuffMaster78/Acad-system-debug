"""
writer_management/models/discipline.py

Discipline event records. All append-only source-of-truth models.

ARCHITECTURE
------------
These models are the SOURCE OF TRUTH for discipline state.
WriterDisciplineState is the CACHE derived from them.

After any write to these models, DisciplineService calls
WriterStatusService.recompute(writer) to rebuild the cache.

Never read these models directly for routing decisions —
read WriterDisciplineState instead.

MODELS
------
WriterDisciplineConfig — site-level thresholds (max strikes, auto days)
WriterStrike — individual strike event (append-only)
WriterSuspension — suspension period record
WriterSuspensionHistory — audit log of suspension changes
WriterBlacklist — blacklist record
WriterBlacklistHistory — audit log of blacklist changes
WriterProbation — probation period record
WriterPenalty — financial penalty tied to an order

WHAT WAS REMOVED
----------------
- All save() Website auto-creation overrides
- lift_suspension() method on WriterSuspension → DisciplineService
- check_expiry() method on Probation → DisciplineService
- unique_together on Suspension and Blacklist → partial UniqueConstraint
- All __str__ referencing writer.user.username → writer.registration_id
- WriterStrikeHistory — redundant, WriterActionLog covers this
"""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class WriterDisciplineConfig(models.Model):
    """
    Site-level discipline thresholds.

    One row per website. Created by admin on site setup.
    Read by DisciplineService and WriterWarningService.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="discipline_config",
    )
    max_strikes_before_warning = models.PositiveIntegerField(
        default=3,
        help_text="Active strikes before admin alert is triggered.",
    )
    auto_suspend_on_strikes = models.PositiveIntegerField(
        default=5,
        help_text=(
            "Active strikes that trigger automatic suspension. "
            "0 = auto-suspension disabled."
        ),
    )
    auto_suspend_days = models.PositiveIntegerField(
        default=7,
        help_text="Duration of auto-triggered suspension in days.",
    )
    auto_blacklist_on_strikes = models.PositiveIntegerField(
        default=10,
        help_text=(
            "Lifetime strikes that trigger automatic blacklisting. "
            "0 = auto-blacklisting disabled."
        ),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Discipline Config"
        verbose_name_plural = "Writer Discipline Configs"

    def __str__(self) -> str:
        return f"DisciplineConfig<{self.website.id}>"


class WriterSuspension(models.Model):
    """
    A suspension period for a writer.

    One active suspension per writer per website at a time.
    Enforced by partial UniqueConstraint.

    Lifted by DisciplineService.lift_suspension() —
    never by calling save() directly.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_suspensions",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="suspensions",
    )
    reason = models.TextField()
    auto_triggered = models.BooleanField(
        default=False,
        help_text="True when triggered by strike threshold, not admin.",
    )
    suspended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_suspensions_issued",
        help_text="Admin who suspended. Null for auto-triggered.",
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When suspension ends. "
            "Null = indefinite — must be lifted manually."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )
    lifted_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_suspensions_lifted",
    )
    lift_reason = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Writer Suspension"
        verbose_name_plural = "Writer Suspensions"
        ordering = ["-start_date"]
        constraints = [
            # Only one active suspension per writer per site
            models.UniqueConstraint(
                fields=["website", "writer"],
                condition=models.Q(is_active=True),
                name="unique_active_suspension_per_writer",
            ),
            # end_date must be after start_date when set
            models.CheckConstraint(
                condition=(
                    models.Q(end_date__isnull=True) |
                    models.Q(end_date__gt=models.F("start_date"))
                ),
                name="suspension_end_after_start",
            ),
            # lifted_at requires is_active=False
            models.CheckConstraint(
                condition=(
                    models.Q(lifted_at__isnull=True) |
                    models.Q(is_active=False)
                ),
                name="suspension_lifted_at_only_if_inactive",
            ),
        ]

    def __str__(self) -> str:
        state = "active" if self.is_active else "lifted"
        return f"WriterSuspension<{self.writer.id}> [{state}]"


class WriterSuspensionHistory(models.Model):
    """
    Append-only audit log of suspension state changes.

    Created by DisciplineService on every suspension event:
    created, extended, lifted, auto-triggered.
    """

    suspension = models.ForeignKey(
        WriterSuspension,
        on_delete=models.CASCADE,
        related_name="history",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="suspension_history_entries",
    )
    change_type = models.CharField(
        max_length=20,
        choices=[
            ("created", "Created"),
            ("extended", "Extended"),
            ("lifted", "Lifted"),
            ("auto_triggered", "Auto-Triggered"),
        ],
    )
    notes = models.TextField(blank=True, default="")
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writer Suspension History"
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return (
            f"SuspensionHistory<{self.suspension.pk}> "
            f"[{self.change_type}] @ {self.changed_at:%Y-%m-%d}"
        )


class WriterBlacklist(models.Model):
    """
    A blacklist record for a writer.

    Blacklisting is the most severe discipline action.
    Supersedes suspension — a blacklisted writer is excluded from
    all routing regardless of suspension state.

    One active blacklist per writer per website at a time.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_blacklists",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="blacklist_entries",
    )
    reason = models.TextField()
    auto_triggered = models.BooleanField(
        default=False,
        help_text="True when triggered by strike threshold.",
    )
    blacklisted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_blacklists_issued",
    )
    blacklisted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    lifted_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_blacklists_lifted",
    )
    lift_reason = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Writer Blacklist"
        verbose_name_plural = "Writer Blacklists"
        ordering = ["-blacklisted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "writer"],
                condition=models.Q(is_active=True),
                name="unique_active_blacklist_per_writer",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(lifted_at__isnull=True) |
                    models.Q(is_active=False)
                ),
                name="blacklist_lifted_at_only_if_inactive",
            ),
        ]

    def __str__(self) -> str:
        trigger = "auto" if self.auto_triggered else "manual"
        state = "active" if self.is_active else "lifted"
        return (
            f"WriterBlacklist<{self.writer.id}> "
            f"[{trigger}|{state}]"
        )


class WriterBlacklistHistory(models.Model):
    """Append-only audit log of blacklist state changes."""

    blacklist = models.ForeignKey(
        WriterBlacklist,
        on_delete=models.CASCADE,
        related_name="history",
    )
    change_type = models.CharField(
        max_length=20,
        choices=[
            ("created", "Created"),
            ("lifted", "Lifted"),
            ("auto_triggered", "Auto-Triggered"),
        ],
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blacklist_history_entries",
    )
    notes = models.TextField(blank=True, default="")
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writer Blacklist History"
        ordering = ["-changed_at"]

    def __str__(self) -> str:
        return (
            f"BlacklistHistory<{self.blacklist.pk}> "
            f"[{self.change_type}]"
        )


class WriterProbation(models.Model):
    """
    A probation period for a writer.

    Less severe than suspension. Writer can still take orders
    but is flagged in the system. Used as an intermediate step
    between warnings and suspension.

    Renamed from Probation → WriterProbation for naming consistency.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_probations",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="probation_records",
    )
    placed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="probations_placed",
        help_text="Admin who placed writer on probation. Null = auto.",
    )
    reason = models.TextField()
    auto_triggered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(
        help_text=(
            "When probation ends. "
            "DisciplineService checks this during daily expiry task."
        ),
    )
    is_active = models.BooleanField(default=True, db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Writer Probation"
        verbose_name_plural = "Writer Probations"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "writer"],
                condition=models.Q(is_active=True),
                name="unique_active_probation_per_writer",
            ),
            models.CheckConstraint(
                condition=models.Q(end_date__gt=models.F("start_date")),
                name="probation_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        state = "active" if self.is_active else "ended"
        return f"WriterProbation<{self.writer.id}> [{state}]"


class WriterPenalty(models.Model):
    """
    A financial penalty applied to a writer for a specific order.

    Recorded here for audit. The actual deduction from earnings
    is handled by writer_compensation — this model is the
    disciplinary record, not the financial transaction.
    """

    class PenaltyReason(models.TextChoices):
        LATE_SUBMISSION = "late_submission", "Late Submission"
        PLAGIARISM = "plagiarism", "Plagiarism"
        MISSED_DEADLINE = "missed_deadline", "Missed Deadline"
        CLIENT_COMPLAINT = "client_complaint", "Client Complaint"
        POLICY_VIOLATION = "policy_violation", "Policy Violation"
        OTHER = "other", "Other"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_penalties",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="penalties",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_penalties",
        help_text="The order this penalty relates to.",
    )
    reason = models.CharField(
        max_length=20,
        choices=PenaltyReason.choices,
    )
    amount_deducted = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Amount to deduct from earnings. "
            "Actual deduction executed by writer_compensation."
        ),
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="penalties_applied",
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Penalty"
        verbose_name_plural = "Writer Penalties"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["writer", "created_at"],
                name="penalty_writer_time_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_deducted__gte=Decimal("0.00")),
                name="penalty_amount_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterPenalty<{self.writer.id}> "
            f"{self.reason} ${self.amount_deducted}"
        )