"""
WriterProfile is the stable writer domain anchor.

It extends accounts.AccountProfile and represents the
persistent identity of a writer inside the platform.

This model intentionally contains ONLY:

Identity
    - registration_id
    - public_uuid
    - pen_name
    - timezone

Classification
    - writer_level

Verification
    - is_verified
    - verification_status

Lifecycle
    - onboarding_status
    - joined_at
    - is_deleted
    - deleted_at

Everything operational lives elsewhere:

    WriterStatus
        Real-time online/offline presence

    WriterCapacity
        Workload and assignment capacity

    WriterDisciplineState
        Suspension and restriction state

    WriterPerformance
        Aggregated writer metrics

    writer_compensation app
        Earnings and financial systems

Identity chain:

  auth.User
    └── accounts.AccountProfile
          └── writer_management.WriterProfile   <- this model
                └── writer_management.WriterLevel
                      └── writer_management.WriterLevelSettings
"""
import uuid
from django.db import models
from django.utils.timezone import now

from writer_management.enums import (
    WriterOnboardingStatus,
    WriterVerificationStatus,
)

class WriterProfile(models.Model):
    """
    Minimal writer domain entity.

    Low-volatility. Cache-friendly. Query-friendly.
    Fields here change rarely — level assignment, verification,
    onboarding progression, soft delete.
 
    High-churn concerns (orders, availability, discipline, metrics)
    live in dedicated models keyed to this one.
 
    Routing eligibility is computed by:
        writer_management.services.assignment_eligibility_service
            .WriterEligibilityService.is_eligible(writer_profile)
    """

    # IDENTITY LINK (single source of truth)
    account_profile = models.OneToOneField(
        "accounts.AccountProfile",
        on_delete=models.CASCADE,
        related_name="writer_profile",
    )

    # STABLE IDENTIFIER
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )

    public_uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        help_text=(
            "Immutable public identifier for API exposure. "
            "Use this in all external URLs and API responses. "
            "Never expose the integer PK."
        ),
    )

    # DOMAIN CLASSIFICATION (cached, not computed)
    writer_level = models.ForeignKey(
        "writer_management.WriterLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writers",
    )

    # IDENTITY DISPLAY
    pen_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=(
            "Writer's display name. "
            "Changed via WriterPenNameChangeRequest — not directly editable "
            "by the writer through the standard profile API."
        ),
    )
 
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text=(
            "IANA timezone string. e.g. 'Africa/Nairobi', 'America/New_York'. "
            "Used by WriterAvailabilityPreference to interpret preferred "
            "working hours in the writer's local time."
        ),
    )

    # Experiennce of the Writer

    bio = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Writer's professional bio shown to clients "
            "during preferred assignment browsing. "
            "Plain text only. Max 500 characters enforced "
            "by WriterProfileSerializer."
        ),
    )

    qualifications = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Academic and professional qualifications. "
            "Schema: ["
            "{'title': str, 'institution': str, 'year': int, 'verified': bool}"
            "]. "
            "Writer submits — admin marks verified=True per entry."
        ),
    )

    years_of_experience = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Years of professional writing experience. "
            "Self-declared by writer. Shown on client-facing card."
        ),
    )
        # ----------------------------------------------------------------
    # CLASSIFICATION
    # Writer level is dynamic. Admins define levels per website.
    # Valid level names live in the WriterLevel table — no enum here.
    # Use LevelSelector.get_active_levels(website) for choices.
    # ----------------------------------------------------------------
 
    writer_level = models.ForeignKey(
        "writer_management.WriterLevel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writers",
        help_text=(
            "Current writer tier. "
            "Rate card resolved via writer_level.settings. "
            "Changed only by level_progression_service. "
            "SET_NULL so profile survives if a level is edited or deactivated — "
            "the level row itself is rarely deleted."
        ),
    )

    # VERIFICATION STATE (manual/admin controlled)
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Admin-controlled. "
            "Some order types require is_verified=True. "
            "Set via the admin verification workflow, "
            "not directly via the API."
        ),
    )
 
    verification_status = models.CharField(
        max_length=20,
        choices=WriterVerificationStatus.choices,
        default=WriterVerificationStatus.UNVERIFIED,
        help_text="Tracks progress through the verification workflow.",
    )
 
    # LIFECYCLE STATE (soft delete pattern)
    onboarding_status = models.CharField(
        max_length=20,
        choices=WriterOnboardingStatus.choices,
        default=WriterOnboardingStatus.NOT_STARTED,
        db_index=True,
        help_text=(
            "Tracks writer onboarding progression. "
            "WriterEligibilityService gates assignment routing on "
            "onboarding_status == COMPLETED. "
            "Managed by accounts.writer_onboarding_service."
        ),
    )
 
    joined_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
 
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Soft delete. Excluded from all routing and API responses. "
            "Historical records (orders, payments, ratings) are preserved. "
            "Set via profile_service.delete_writer() — never directly."
        ),
    )
 
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )
 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Profile"
        verbose_name_plural = "Writer Profiles"
        ordering = ["-joined_at"]
        indexes = [
            # Eligibility service entry filter
            models.Index(
                fields=["is_deleted", "onboarding_status"],
                name="writer_prof_eligibility_idx",
            ),
            # Level-based reporting and routing
            models.Index(
                fields=["writer_level", "is_deleted"],
                name="writer_prof_level_idx",
            ),
            # Verification dashboard
            models.Index(
                fields=["is_verified", "verification_status"],
                name="writer_prof_verification_idx",
            ),
        ]
        constraints = [
            # Soft delete integrity:
            # if is_deleted is True, deleted_at must be set
            models.CheckConstraint(
                check=(
                    models.Q(is_deleted=False) |
                    models.Q(deleted_at__isnull=False)
                ),
                name="writer_prof_deleted_has_timestamp",
            ),
            # Verification integrity:
            # is_verified=True implies status must be VERIFIED
            models.CheckConstraint(
                check=(
                    models.Q(is_verified=False) |
                    models.Q(
                        verification_status=WriterVerificationStatus.VERIFIED
                    )
                ),
                name="writer_prof_verified_implies_status",
            ),
        ]
 

    def __str__(self) -> str:
        return self.registration_id
    

    # CONVENIENCE — no logic, no DB queries

    @property
    def onboarding_completed(self) -> bool:
        """
        Read-only convenience. Use onboarding_status directly
        in querysets — this property is for single-instance checks only.
        """
        return self.onboarding_status == WriterOnboardingStatus.COMPLETED
 
    @property
    def is_onboarding_failed(self) -> bool:
        return self.onboarding_status == WriterOnboardingStatus.REJECTED

    # IDENTITY SNAPSHOT — admin UI presentation only
    # Not for API serialization. Not for business logic.

    def get_identity_snapshot(self) -> dict:
        """
        Lightweight presentation helper for admin interfaces.

        Not intended for:
            - business logic
            - serializers
            - routing decisions
        """
        return {
            "public_uuid": str(self.public_uuid),
            "registration_id": self.registration_id,
            "pen_name": self.pen_name or None,
            "timezone": self.timezone,
            "bio": self.bio or None,
            "qualifications": self.qualifications,
            "years_of_experience": self.years_of_experience,
            "writer_level_id": (
                self.writer_level.pk
                if self.writer_level
                else None
            ),
            "writer_level_name": (
                self.writer_level.name
                if self.writer_level
                else None
            ),
            "is_verified": self.is_verified,
            "verification_status": (
                self.verification_status
            ),
            "onboarding_status": (
                self.onboarding_status
            ),
            "joined_at": self.joined_at,
            "is_deleted": self.is_deleted,
        }
 