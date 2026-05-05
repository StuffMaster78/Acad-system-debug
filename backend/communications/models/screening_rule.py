from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationScreeningMatchType:
    """
    Supported screening match strategies.
    """

    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"

    CHOICES = (
        (EXACT, "Exact"),
        (CONTAINS, "Contains"),
        (REGEX, "Regex"),
    )


class CommunicationScreeningAction:
    """
    Actions taken when a screening rule matches.
    """

    MASK = "mask"
    FLAG = "flag"
    HOLD_FOR_REVIEW = "hold_for_review"
    HIDE = "hide"
    BLOCK = "block"

    CHOICES = (
        (MASK, "Mask"),
        (FLAG, "Flag"),
        (HOLD_FOR_REVIEW, "Hold for review"),
        (HIDE, "Hide"),
        (BLOCK, "Block"),
    )


class CommunicationScreeningSeverity:
    """
    Screening rule severity levels.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    CHOICES = (
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (CRITICAL, "Critical"),
    )


class CommunicationScreeningRule(models.Model):
    """
    Tenant scoped rule for screening unsafe message content.

    Admins and superadmins can use this to block or flag words,
    phrases, links, or regular expression patterns.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_screening_rules",
        null=True,
        blank=True,
        help_text="Leave empty for a platform wide rule.",
    )

    name = models.CharField(max_length=120)
    pattern = models.CharField(max_length=255)

    match_type = models.CharField(
        max_length=20,
        choices=CommunicationScreeningMatchType.CHOICES,
        default=CommunicationScreeningMatchType.CONTAINS,
    )
    action = models.CharField(
        max_length=30,
        choices=CommunicationScreeningAction.CHOICES,
        default=CommunicationScreeningAction.FLAG,
    )
    severity = models.CharField(
        max_length=20,
        choices=CommunicationScreeningSeverity.CHOICES,
        default=CommunicationScreeningSeverity.MEDIUM,
    )

    replacement_text = models.CharField(max_length=80, default="*****")
    reason = models.CharField(max_length=120, blank=True)

    is_active = models.BooleanField(default=True)
    is_platform_rule = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_communication_screening_rules",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_communication_screening_rules",
    )

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "match_type"]),
            models.Index(fields=["website", "action"]),
            models.Index(fields=["is_platform_rule", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_comm_screening_rule_name_per_website",
            ),
        ]

    def __str__(self) -> str:
        return self.name