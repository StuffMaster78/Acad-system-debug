"""
Pre-onboarding writer application pipeline.

LIFECYCLE
---------
A WriterApplication exists BEFORE WriterProfile.
It represents a candidate applying to become a writer on the platform.

Pipeline:

    1. Candidate submits application (status=PENDING)
       WriterApplication created. No AccountProfile yet.

    2. Admin reviews (status=UNDER_REVIEW)
       Admin marks under review. Application is being assessed.

    3a. Admin approves (status=APPROVED)
        WriterApplicationService.approve() is called.
        → AccountProfile created (or linked if user pre-registered)
        → WriterProfile created
        → Onboarding email sent
        → WriterApplication.account_profile linked

    3b. Admin rejects (status=REJECTED)
        WriterApplicationService.reject() called.
        → rejection_reason recorded
        → Rejection email sent to candidate

    4. Candidate withdraws (status=WITHDRAWN)
        Candidate cancels their own application before review completes.

MULTI-TENANCY
-------------
Applications are website-specific. A writer can apply to multiple
websites and have separate applications for each.

UNIQUENESS
----------
One active (non-withdrawn, non-rejected) application per email per website.
A rejected writer can reapply — a new application row is created.

RELATIONSHIP TO WriterProfile
------------------------------
WriterApplication is the gateway to WriterProfile.
After approval, account_profile is linked and WriterProfile is created.
The application is retained as the original onboarding record.
"""

from django.conf import settings
from django.db import models


class WriterApplication(models.Model):
    """
    Writer onboarding application — exists before WriterProfile.

    Submitted by the candidate. Reviewed by admin.
    On approval, triggers WriterProfile creation.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_applications",
        help_text="Which website this application is for.",
    )

    # Linked after approval — null until then
    account_profile = models.OneToOneField(
        "accounts.AccountProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_application",
        help_text=(
            "Linked when the application is approved and "
            "AccountProfile is created or matched."
        ),
    )

    # ----------------------------------------------------------------
    # APPLICANT INFORMATION
    # Captured at application time — independent of any User account.
    # ----------------------------------------------------------------

    full_name = models.CharField(max_length=255)

    email = models.EmailField(
        db_index=True,
        help_text="Primary contact email for this application.",
    )

    phone_number = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )

    country = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    # ----------------------------------------------------------------
    # QUALIFICATIONS
    # ----------------------------------------------------------------

    education_level = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Highest level of education completed.",
    )

    years_of_experience = models.PositiveSmallIntegerField(
        default=0,
        help_text="Years of professional writing experience.",
    )

    subjects = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Subject areas the applicant specialises in. "
            "Schema: [str]. e.g. ['Economics', 'Statistics']"
        ),
    )

    # ----------------------------------------------------------------
    # APPLICATION CONTENT
    # ----------------------------------------------------------------

    application_text = models.TextField(
        blank=True,
        default="",
        help_text="Applicant's cover letter / motivation statement.",
    )

    resume = models.FileField(
        upload_to="writer_applications/resumes/",
        null=True,
        blank=True,
    )

    sample_work = models.FileField(
        upload_to="writer_applications/samples/",
        null=True,
        blank=True,
        help_text="Writing sample submitted with the application.",
    )

    # ----------------------------------------------------------------
    # STATUS AND REVIEW
    # ----------------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_writer_applications",
        help_text="Admin who reviewed this application.",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the review decision was made.",
    )

    rejection_reason = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Required when status=REJECTED. "
            "Shown to the applicant in the rejection notification."
        ),
    )

    admin_notes = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Internal admin notes on this application. "
            "Not shown to the applicant."
        ),
    )

    # ----------------------------------------------------------------
    # AUDIT
    # ----------------------------------------------------------------

    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Application"
        verbose_name_plural = "Writer Applications"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(
                fields=["website", "status", "submitted_at"],
                name="writer_app_site_status_idx",
            ),
            models.Index(
                fields=["email", "website"],
                name="writer_app_email_site_idx",
            ),
        ]
        constraints = [
            # Only one active application per email per website
            # (active = not withdrawn, not rejected)
            models.UniqueConstraint(
                fields=["email", "website"],
                condition=models.Q(
                    status__in=["pending", "under_review", "approved"]
                ),
                name="unique_active_application_per_email_per_site",
            ),
            # Review integrity: approved/rejected must have reviewer
            models.CheckConstraint(
                condition=(
                    ~models.Q(status__in=["approved", "rejected"]) |
                    models.Q(reviewed_by__isnull=False)
                ),
                name="writer_app_reviewed_has_reviewer",
            ),
            # Review integrity: approved/rejected must have timestamp
            models.CheckConstraint(
                condition=(
                    ~models.Q(status__in=["approved", "rejected"]) |
                    models.Q(reviewed_at__isnull=False)
                ),
                name="writer_app_reviewed_has_timestamp",
            ),
            # Rejection integrity: rejected must have reason
            # (enforced in service — cannot check text non-empty in SQL)
        ]

    def __str__(self) -> str:
        return (
            f"WriterApplication<{self.email}> "
            f"[{self.status}] @ {self.submitted_at:%Y-%m-%d}"
        )

    @property
    def is_active(self) -> bool:
        """True if application is still in progress."""
        return self.status in (
            self.Status.PENDING,
            self.Status.UNDER_REVIEW,
        )

    @property
    def is_terminal(self) -> bool:
        """True if application has reached a final state."""
        return self.status in (
            self.Status.APPROVED,
            self.Status.REJECTED,
            self.Status.WITHDRAWN,
        )