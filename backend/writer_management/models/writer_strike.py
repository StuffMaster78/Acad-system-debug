"""
Permanent disciplinary strikes for serious policy violations.

WHAT A STRIKE IS
----------------
A permanent formal record for serious misconduct that cannot
be corrected by simply changing behaviour.
Examples:
    - Confirmed plagiarism (Turnitin evidence)
    - Off-platform client solicitation
    - Academic misconduct (completing exam papers)
    - Abusive behaviour toward clients
    - Identity fraud / account sharing
    - Repeated severe violations after warnings failed

WHAT A STRIKE IS NOT
---------------------
A strike is NOT a warning.
Warnings are for correctable behaviour — they expire.
Strikes are permanent — they count toward the lifetime
blacklist threshold regardless of when they occurred.

KEY PROPERTIES
--------------
- Permanent: strikes never expire
- Cumulative: lifetime count determines blacklist eligibility
- Voidable: admin can void a strike issued in error
  (the record stays — voiding just removes it from thresholds)
- Auditable: full void trail preserved

THRESHOLD EVALUATION
--------------------
DisciplineService evaluates after every new strike:

    lifetime_active_strikes >= auto_suspend_on_strikes
        → DisciplineService.suspend() (if not already suspended)

    lifetime_active_strikes >= auto_blacklist_on_strikes
        → DisciplineService.blacklist()

"Active" means is_voided=False.
Lifetime count includes all non-voided strikes, regardless of age.

DIFFERENCE FROM WARNINGS IN THRESHOLD LOGIC
--------------------------------------------
    Warnings  → count ACTIVE (non-expired, non-voided) warnings
                 A warning from 6 months ago that expired does NOT count
    Strikes   → count LIFETIME non-voided strikes
                 A strike from 2 years ago STILL counts

This is intentional. A writer who plagiarised 2 years ago and
plagiarises again today has demonstrated a pattern that warnings
and time cannot excuse.

OWNERSHIP
---------
Created by: DisciplineService.issue_strike()
Voided by:  DisciplineService.void_strike()
Read by:    WriterStatusService.recompute()
            DisciplineService._evaluate_strike_thresholds()
"""

from django.conf import settings
from django.db import models


class WriterStrike(models.Model):
    """
    A permanent disciplinary strike against a writer.

    Append-only except for the void fields.
    Never deleted. Voiding is the only correction mechanism.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_strikes",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="strikes",
    )
    # WHAT HAPPENED
    reason = models.TextField(
        help_text=(
            "Full description of the violation. "
            "Include evidence references (Turnitin report ID, "
            "message thread ID, order number, investigation notes). "
            "This is an internal record — not shown to writer by default."
        ),
    )
    category = models.CharField(
        max_length=30,
        choices=[
            ("plagiarism",          "Plagiarism"),
            ("off_platform",        "Off-Platform Solicitation"),
            ("academic_misconduct", "Academic Misconduct"),
            ("abusive_behaviour",   "Abusive Behaviour"),
            ("identity_fraud",      "Identity Fraud / Account Sharing"),
            ("repeated_violation",  "Repeated Serious Violation"),
            ("other",               "Other"),
        ],
        default="other",
        db_index=True,
        help_text="Category for analytics and admin reporting.",
    )

    # Reference to supporting evidence
    evidence_notes = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Internal reference to evidence: report IDs, screenshots, "
            "order numbers, investigation ticket numbers. "
            "Not shown to writer."
        ),
    )

    # WHO ISSUED IT
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_writer_strikes",
        help_text="Admin who issued the strike. Null = system-triggered.",
    )

    # ----------------------------------------------------------------
    # VOID MECHANISM
    # Used when a strike was issued in error.
    # Example: plagiarism strike voided after Turnitin false positive
    # confirmed — similarity was to writer's own previously submitted work.
    #
    # Voided strikes:
    #   - Do NOT count toward any threshold
    #   - Are NOT deleted
    #   - Remain visible in admin audit log
    #   - Are shown with "voided" status
    # ----------------------------------------------------------------

    is_voided = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "True when strike was voided by senior admin due to error. "
            "Voided strikes do not count toward suspension or blacklist "
            "thresholds. The record is preserved for audit."
        ),
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voided_writer_strikes",
    )
    void_reason = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Why the strike was voided. "
            "Must be provided. Include investigation outcome."
        ),
    )

    # ----------------------------------------------------------------
    # WRITER NOTIFICATION
    # Track whether the writer was formally notified.
    # ----------------------------------------------------------------

    writer_notified = models.BooleanField(
        default=False,
        help_text=(
            "True once the writer has been formally notified "
            "of this strike via the notification system."
        ),
    )
    notified_at = models.DateTimeField(null=True, blank=True)

    # ----------------------------------------------------------------
    # AUDIT
    # ----------------------------------------------------------------

    issued_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Strike"
        verbose_name_plural = "Writer Strikes"
        ordering = ["-issued_at"]
        indexes = [
            # Primary threshold query: active strikes for a writer
            models.Index(
                fields=["writer", "is_voided"],
                name="strike_writer_active_idx",
            ),
            # Admin dashboard: strikes by category across site
            models.Index(
                fields=["website", "category", "issued_at"],
                name="strike_site_category_idx",
            ),
        ]
        constraints = [
            # Void integrity: voided strikes must have timestamp
            models.CheckConstraint(
                check=(
                    models.Q(is_voided=False) |
                    models.Q(voided_at__isnull=False)
                ),
                name="strike_voided_has_timestamp",
            ),
            # Notification integrity: notified_at requires writer_notified
            models.CheckConstraint(
                check=(
                    models.Q(writer_notified=False) |
                    models.Q(notified_at__isnull=False)
                ),
                name="strike_notified_has_timestamp",
            ),
        ]

    def __str__(self) -> str:
        state = "voided" if self.is_voided else "active"
        return (
            f"WriterStrike<{self.writer.id}> "
            f"[{self.category}|{state}] "
            f"@ {self.issued_at:%Y-%m-%d}"
        )

    # ----------------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------------

    @property
    def counts_toward_threshold(self) -> bool:
        """
        True if this strike is counted in threshold evaluations.
        Voided strikes are excluded from all threshold counts.
        """
        return not self.is_voided