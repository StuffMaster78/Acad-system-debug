from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class FeedbackRequest(models.Model):
    CATEGORY_CHOICES = [
        # Client
        ("orders", "Orders"),
        ("payments", "Payments & Billing"),
        ("client_experience", "Client Experience"),
        ("file_delivery", "File Delivery"),
        ("communication", "Communication"),
        # Writer
        ("writer_workflow", "Writer Workflow"),
        ("payout_earnings", "Payout & Earnings"),
        ("bidding", "Bidding & Queue"),
        ("workload", "Workload Management"),
        # Shared
        ("classes", "Classes"),
        ("special_orders", "Special Orders"),
        # Staff
        ("cms", "CMS & Content"),
        ("analytics", "Analytics & Reporting"),
        ("support_tools", "Support Tools"),
        ("admin_tools", "Admin Tools"),
        ("automation", "Automation & SLA"),
        ("permissions", "Permissions & Roles"),
        # Universal
        ("bug_report", "Bug Report"),
        ("other", "Other"),
    ]

    REQUEST_TYPE_CHOICES = [
        ("feature_request", "Feature Request"),
        ("improvement", "Improvement"),
        ("bug_report", "Bug Report"),
        ("question", "Question"),
    ]

    STATUS_CHOICES = [
        ("new", "New"),
        ("triaging", "Triaging"),
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("released", "Released"),
        ("declined", "Declined"),
        ("duplicate", "Duplicate"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    SURFACE_CHOICES = [
        ("client", "Client"),
        ("writer", "Writer"),
        ("staff", "Staff"),
    ]

    # Tenant + submitter
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="feedback_requests",
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_submitted",
    )
    requester_role = models.CharField(max_length=20)
    portal_surface = models.CharField(max_length=20, choices=SURFACE_CHOICES)

    # Content
    title = models.CharField(max_length=255)
    description = models.TextField()
    request_type = models.CharField(
        max_length=20, choices=REQUEST_TYPE_CHOICES, default="feature_request"
    )
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="other"
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )

    # Workflow
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new"
    )
    staff_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_owned",
    )

    # Engagement (denormalised for fast sorting)
    upvote_count = models.PositiveIntegerField(default=0)

    # Duplicate tracking
    duplicate_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
    )

    # Optional linked objects (IDs only — avoids FK coupling across apps)
    linked_order_id = models.PositiveIntegerField(null=True, blank=True)
    linked_ticket_id = models.PositiveIntegerField(null=True, blank=True)

    # Staff-only triage field
    internal_notes = models.TextField(blank=True, default="")

    # Public staff response
    public_response = models.TextField(blank=True, default="")
    public_response_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_responses",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "portal_surface", "status"]),
            models.Index(fields=["requester", "created_at"]),
            models.Index(fields=["status", "category"]),
        ]

    def __str__(self) -> str:
        return f"[{self.status}] {self.title} ({self.requester_role})"


class FeedbackVote(models.Model):
    """One upvote per user per request. Toggle — adding again removes."""

    request = models.ForeignKey(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="votes",
    )
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_votes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("request", "voter")

    def __str__(self) -> str:
        return f"{self.voter_id} → #{self.request_id}"


class FeedbackStatusEvent(models.Model):
    """Immutable audit log of every status change."""

    request = models.ForeignKey(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"#{self.request_id}: {self.from_status} → {self.to_status}"
