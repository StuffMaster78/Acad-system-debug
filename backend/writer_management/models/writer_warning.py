"""
Formal warnings issued to writers for correctable behaviour.
 
WHAT A WARNING IS
-----------------
A temporary formal notice for behaviour that can be corrected.
Examples:
    - Late delivery (first offence)
    - Communication failure during active order
    - Unprofessional revision handling
    - Accepting orders outside verified expertise
    - Availability abuse
 
WHAT A WARNING IS NOT
---------------------
A warning is NOT a strike.
Strikes are for serious, permanent policy violations (plagiarism,
fraud, off-platform solicitation). See discipline.py.
 
KEY PROPERTIES
--------------
- Temporary: warnings expire after a configured duration
- Revocable: admin can void a warning issued in error
- Countable: active warning count triggers escalation thresholds
- Auditable: full revocation trail preserved
 
ACTIVE WARNING DEFINITION
--------------------------
A warning is active when ALL of the following are true:
    is_active=True
    is_voided=False
    expires_at is None OR expires_at > now()
 
ESCALATION
----------
WriterWarningService evaluates thresholds from
WriterWarningEscalationConfig after every new warning:
 
    active_warnings >= admin_alert_threshold
        → notify admins
 
    active_warnings >= auto_probation_threshold
        → DisciplineService.place_on_probation()
 
    active_warnings >= auto_suspension_threshold
        → DisciplineService.suspend()
 
WriterDisciplineState caches active_warning_count and
lifetime_warning_count for fast eligibility checks.
 
OWNERSHIP
---------
Created by: WriterWarningService.issue_warning()
Revoked by: WriterWarningService.revoke_warning()
Read by:    WriterStatusService.recompute()
            WriterEligibilityService (via WriterDisciplineState)
"""

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class WriterWarning(models.Model):
    """
    A formal warning issued to a writer.

    Append-only. Never updated after creation except is_active
    (for manual revocation by admin).

    Active warning definition:
        is_active=True AND (expires_at is None OR expires_at > now())

    Escalation thresholds are evaluated by WriterWarningService
    after every new warning. The service counts active warnings
    and compares against WriterWarningEscalationConfig thresholds.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_warnings",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="warnings",
    )
    reason = models.TextField(
        help_text=(
            "Full description of the behaviour that triggered this warning. "
            "Include order number, date, and specific policy violated. "
            "This text is shown to the writer."
        ),
    )
    category = models.CharField(
        max_length=30,
        choices=[
            ("late_delivery",      "Late Delivery"),
            ("communication",      "Communication Failure"),
            ("quality",            "Quality Issue"),
            ("availability",       "Availability Abuse"),
            ("revision_handling",  "Revision Handling"),
            ("policy_violation",   "Policy Violation"),
            ("other",              "Other"),
        ],
        default="other",
        db_index=True,
        help_text="Category for analytics and threshold evaluation.",
    )
    # Who issued the warning
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_writer_warnings",
        help_text="Admin who issued the warning. Null = system-triggered.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Set to False when manually revoked by admin. "
            "Time-based expiry is handled by expires_at — do not "
            "set this False to expire a warning, let expires_at do it."
        ),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "When this warning stops counting toward thresholds. "
            "Null means it never expires (permanent warning)."
            "Default is set from WriterWarningEscalationConfig."
            "default_warning_duration_days."
        ),
    )

    # REVOCATION
    # Used when a warning was issued in error.
    # Revoked warnings are preserved for audit — never deleted.
    is_voided = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "True when warning was voided by admin due to error. "
            "Voided warnings do not count toward any threshold. "
            "Use this instead of deletion to preserve the audit trail."
        ),
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    voided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voided_writer_warnings",
    )
    void_reason = models.TextField(
        blank=True,
        default="",
        help_text="Why the warning was voided. Required when is_voided=True.",
    )

    # Audit Meta
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Warning"
        verbose_name_plural = "Writer Warnings"
        ordering = ["-created_at"]
        indexes = [
            # Primary query: active warnings for a writer
            models.Index(
                fields=["writer", "is_active", "expires_at"],
                name="writer_warning_active_idx",
            ),
             # Admin dashboard: warnings by category across site
            models.Index(
                fields=["website", "category", "created_at"],
                name="writer_warning_site_time_idx",
            ),
        ]

        constraints = [
            # Void integrity: voided warnings must have a timestamp
            models.CheckConstraint(
                condition=(
                    models.Q(is_voided=False) |
                    models.Q(voided_at__isnull=False)
                ),
                name="warning_voided_has_timestamp",
            ),
            # Void integrity: voided warnings must have a reason
            # (enforced in service — cannot express text non-empty in SQL)
 
            # Inactive integrity: if is_active=False, must be voided
            # OR expires_at must be in the past
            # (partial logic — service enforces, constraint catches gross errors)
            models.CheckConstraint(
                condition=(
                    models.Q(is_active=True) |
                    models.Q(is_voided=True) |
                    models.Q(expires_at__isnull=False)
                ),
                name="warning_inactive_has_expiry_or_void",
            ),
        ]

    def __str__(self) -> str:
        if self.is_voided:
            state = "voided"
        elif not self.is_currently_active:
            state = "expired"
        else:
            state = "active"
        return (
            f"WriterWarning<{self.writer.id}> "
            f"[{self.category}|{state}] "
            f"@ {self.created_at:%Y-%m-%d}"
        )

    # PROPERTIES — single-instance checks only
    # Services use querysets for bulk operations.
    @property
    def is_currently_active(self) -> bool:
        """
        True if this warning currently counts toward escalation thresholds.
 
        Conditions:
            is_active=True
            AND is_voided=False
            AND (expires_at is None OR expires_at > now())
        """
        if not self.is_active:
            return False
        if self.is_voided:
            return False
        if self.expires_at is None:
            return True
        return self.expires_at > now()
 
    @property
    def is_expired(self) -> bool:
        """True if warning has passed its expiry date."""
        if self.expires_at is None:
            return False
        return self.expires_at <= now()
 
    @property
    def days_remaining(self) -> int | None:
        """
        Days until this warning expires.
        None if warning never expires.
        0 if already expired.
        """
        if self.expires_at is None:
            return None
        delta = self.expires_at - now()
        return max(0, delta.days)