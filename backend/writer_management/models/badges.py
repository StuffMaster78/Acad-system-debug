from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from websites.models.websites import Website


class Badge(models.Model):
    """Represents a badge that can be awarded to writers."""

    TYPE_CHOICES = [
        ("performance", "Performance"),
        ("loyalty", "Loyalty"),
        ("behavioral", "Behavioral"),
        ("special", "Special"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="badges",
        help_text="Website that owns this badge configuration.",
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emoji, icon name, or asset key.",
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="performance",
    )
    auto_award = models.BooleanField(default=True)
    description = models.TextField()
    rule_code = models.SlugField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Stable internal slug, e.g. consistent_pro.",
    )
    rule_description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_badges",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "rule_code"],
                name="unique_badge_rule_code_per_website",
            ),
        ]

    def clean(self):
        """Validate badge configuration."""
        if self.auto_award and not self.rule_code:
            raise ValidationError(
                {"rule_code": "Auto-awarded badges must have a rule_code."}
            )

    def __str__(self):
        return f"{self.icon or ''} {self.name}"
    
class WriterBadge(models.Model):
    """Represents a badge awarded to a writer."""

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="badges",
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="writer_badges",
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    is_auto_awarded = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.TextField(blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="revoked_writer_badges",
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ["-issued_at"]
        unique_together = ("writer", "badge", "issued_at")
        constraints = [
            models.UniqueConstraint(
                fields=["writer", "badge"],
                condition=Q(revoked=False),
                name="unique_active_badge_per_writer",
            ),
        ]

    def __str__(self):
        status = "Revoked" if self.revoked else "Active"
        return f"{self.writer} → {self.badge.name} ({status})"
