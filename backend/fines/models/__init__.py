"""
Fines models package.
All models are defined here - both legacy models (moved from models.py)
and new models (from submodules).
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator

# Import new models from submodules first (they may depend on base classes)
from .late_fine_policy import LatenessFineRule
from .fine_type_config import FineTypeConfig

# ============================================================================
# LEGACY MODELS (moved from fines/models.py)
# ============================================================================

class FineType(models.TextChoices):
    """
    Legacy enum of fine types - maintained for backward compatibility.
    New system uses FineTypeConfig for admin-configurable fine types.
    """

    LATE_SUBMISSION = "late_submission", "Late Submission"
    QUALITY = "quality", "Quality Penalty"
    PLAGIARISM = "plagiarism", "Plagiarism"
    INACTIVITY = "inactivity", "Inactivity/Abandonment"
    COMM_BREACH = "comm_breach", "Communication Breach"
    EXCESSIVE_REVISIONS = "excessive_revisions", "Excessive Revisions"
    EXTENSION_OVERUSE = "extension_overuse", "Deadline Extension Overuse"
    MANUAL_VIOLATION = "manual_violation", "Manual Violation"
    PRIVACY_VIOLATION = "privacy_violation", "Privacy Violation"
    LATE_REASSIGNMENT = "late_reassignment", "Late Reassignment Request"
    DROPPING_ORDER_LATE = "dropping_order_late", "Dropping Order Late"
    WRONG_FILES = "wrong_files", "Uploaded Wrong Files"


class FineStatus(models.TextChoices):
    """Enum for the lifecycle status of a fine."""

    ISSUED = "issued", "Issued"
    APPEALED = "appealed", "Appealed"
    DISPUTED = "disputed", "Disputed"
    ESCALATED = "escalated", "Escalated"
    RESOLVED = "resolved", "Resolved"
    WAIVED = "waived", "Waived"
    VOIDED = "voided", "Voided"


class FinePolicy(models.Model):
    """Defines configurable fine rules and percentages over time.

    Attributes:
        fine_type (str): The fine category this policy applies to.
        percentage (Decimal): Percentage of base amount to fine.
        fixed_amount (Decimal): Fixed amount to fine (overrides percentage).
        start_date (DateTime): When this policy becomes active.
        end_date (DateTime): When this policy expires.
        active (bool): Whether the policy is currently active.
        description (str): Admin notes about this policy.
    """

    fine_type = models.CharField(
        max_length=30, choices=FineType.choices, db_index=True
    )
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    fixed_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fines_waived",
        help_text="User who waived the fine, if applicable."
    )
    waived_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the fine was waived."
    )
    waiver_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason given for waiving the fine."
    )

    class Meta:
        ordering = ["-start_date"]
        indexes = [models.Index(fields=["fine_type", "start_date"])]

    def __str__(self):
        return (
            f"{self.get_fine_type_display()} Policy "
            f"({self.start_date:%Y-%m-%d} to "
            f"{self.end_date:%Y-%m-%d if self.end_date else 'ongoing'})"
        )

    def is_active(self):
        """Returns True if the policy is currently active."""
        now = timezone.now()
        if not self.active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True


class Fine(models.Model):
    """
    Represents a fine imposed on a writer for an order.
    
    A fine can be issued automatically (e.g., for late submission) or manually by an admin.
    Writers can dispute fines, which creates a FineAppeal.
    Admins can waive or void fines.
    """

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="fines",
        help_text="The order this fine is associated with."
    )
    
    # Fine type - legacy enum (for backward compatibility)
    fine_type = models.CharField(
        max_length=30,
        choices=FineType.choices,
        null=True,
        blank=True,
        db_index=True,
        help_text="Legacy fine type enum (for backward compatibility)"
    )
    
    # New system: admin-configurable fine type
    fine_type_config = models.ForeignKey(
        'fines.FineTypeConfig',
        on_delete=models.PROTECT,
        related_name='fines',
        null=True,
        blank=True,
        help_text="Admin-configurable fine type (preferred)"
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(help_text="Detailed reason for the fine.")
    
    status = models.CharField(
        max_length=20,
        choices=FineStatus.choices,
        default=FineStatus.ISSUED,
        db_index=True
    )
    
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fines_issued",
        help_text="User who issued the fine (null for system-issued fines)."
    )
    
    imposed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the fine was issued."
    )
    
    # Waiver fields
    resolved = models.BooleanField(
        default=False,
        help_text="Whether this fine has been resolved (waived, voided, or resolved)."
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the fine was resolved."
    )
    resolved_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for resolution."
    )
    waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fines_waived_by_user",
        help_text="User who waived the fine, if applicable."
    )
    waived_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the fine was waived."
    )
    waiver_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason given for waiving the fine."
    )

    class Meta:
        ordering = ["-imposed_at"]
        indexes = [
            models.Index(fields=["order", "status"]),
            models.Index(fields=["status", "imposed_at"]),
            models.Index(fields=["fine_type"]),
            models.Index(fields=["fine_type_config"]),
        ]

    def __str__(self):
        fine_type_name = self.fine_type_config.name if self.fine_type_config else self.get_fine_type_display() if self.fine_type else "Unknown"
        return f"Fine #{self.id} - {fine_type_name} - ${self.amount} ({self.get_status_display()})"

    def is_active(self):
        """Returns True if the fine is still active (not waived/voided/resolved)."""
        return not self.resolved and self.status not in [FineStatus.WAIVED, FineStatus.VOIDED, FineStatus.RESOLVED]


class FineAppeal(models.Model):
    """
    Represents a writer's appeal/dispute of a fine.
    
    Writers can submit appeals with evidence/reasoning.
    Admins can review appeals and accept (waive fine) or reject (uphold fine).
    Appeals can be escalated for higher-level review.
    """

    fine = models.OneToOneField(
        Fine,
        on_delete=models.CASCADE,
        related_name="appeal",
        help_text="The fine being appealed."
    )
    
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fine_appeals",
        help_text="Writer who submitted the appeal.",
        null=True,
        blank=True
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    reason = models.TextField(
        help_text="Writer's explanation for why the fine should be waived."
    )
    
    evidence = models.TextField(
        blank=True,
        help_text="Any additional evidence or context provided by the writer."
    )
    
    # Appeal status (tracks the fine's status changes)
    status = models.CharField(
        max_length=20,
        choices=FineStatus.choices,
        default=FineStatus.DISPUTED,
        help_text="Current status of the appeal (tracks fine status)."
    )
    
    # Escalation fields
    escalated = models.BooleanField(
        default=False,
        help_text="Whether this appeal has been escalated for higher-level review."
    )
    escalated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalated_appeals",
        help_text="Admin/support user this appeal was escalated to."
    )
    escalated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the appeal was escalated."
    )
    escalation_reason = models.TextField(
        blank=True,
        help_text="Reason for escalation."
    )
    
    # Review fields
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appeals_reviewed",
        help_text="Admin who reviewed the appeal."
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the appeal was reviewed."
    )
    review_decision = models.CharField(
        max_length=20,
        choices=[
            ("accepted", "Accepted (Fine Waived)"),
            ("rejected", "Rejected (Fine Upheld)"),
            ("pending", "Pending Review"),
        ],
        default="pending",
        help_text="Decision made on the appeal."
    )
    review_notes = models.TextField(
        blank=True,
        help_text="Admin's notes on the review decision."
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text="Final resolution notes after appeal is closed."
    )

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["fine", "status"]),
            models.Index(fields=["submitted_by", "submitted_at"]),
            models.Index(fields=["status", "reviewed_at"]),
        ]

    def __str__(self):
        return f"Appeal for Fine #{self.fine.id} by {self.submitted_by.username} ({self.get_review_decision_display()})"


class FineAppealEvent(models.Model):
    """
    Timeline entry for a fine appeal capturing status updates,
    evidence uploads, and admin responses.
    """

    EVENT_TYPES = [
        ("appeal_submitted", "Appeal Submitted"),
        ("writer_update", "Writer Update"),
        ("evidence_added", "Evidence Added"),
        ("admin_response", "Admin Response"),
        ("status_change", "Status Update"),
        ("system", "System Notice"),
    ]

    appeal = models.ForeignKey(
        FineAppeal,
        on_delete=models.CASCADE,
        related_name="events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fine_appeal_events",
    )
    actor_role = models.CharField(max_length=32, blank=True)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES)
    message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_event_type_display()} - Appeal #{self.appeal_id}"


class FineAppealEvidence(models.Model):
    """
    File uploads tied to a fine appeal (and optionally a specific event).
    """

    appeal = models.ForeignKey(
        FineAppeal,
        on_delete=models.CASCADE,
        related_name="evidence_files",
    )
    event = models.ForeignKey(
        FineAppealEvent,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fine_appeal_evidence",
    )
    description = models.CharField(max_length=255, blank=True)
    file = models.FileField(
        upload_to="uploads/fine_appeals/%Y/%m/%d/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx", "png", "jpg", "jpeg", "txt", "zip"])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        filename = self.file.name.split("/")[-1]
        return f"Evidence {filename} for Appeal #{self.appeal_id}"


# Export all models
__all__ = [
    # Enums
    'FineType',
    'FineStatus',
    # Legacy models
    'FinePolicy',
    'Fine',
    'FineAppeal',
    'FineAppealEvent',
    'FineAppealEvidence',
    # New models from submodules
    'LatenessFineRule',
    'FineTypeConfig',
]
