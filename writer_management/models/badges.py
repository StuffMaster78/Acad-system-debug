from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from django.utils.timezone import now

class Badge(models.Model):
    """Represents a badge that can be awarded to writers."""
    TYPE_CHOICES = [
        ("performance", "Performance"),
        ("loyalty", "Loyalty"),
        ("behavioral", "Behavioral"),
        ("special", "Special"),
    ]
    Website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="badges",
        null=True,
        blank=True,
        help_text="Optional website context for the badge"
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(
        max_length=10, help_text="e.g. 🧠, 💼, 🧹"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="performance"
    )
    auto_award = models.BooleanField(default=True)
    description = models.TextField()
    rule_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Internal logic slug (e.g. top_10_3_weeks)"
    )
    rule_description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="created_badges"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["-created_at"]
        unique_together = ("name", "type")

    def __str__(self):
        return f"{self.icon or ''} {self.name}"


class WriterBadge(models.Model):
    """Represents a badge awarded to a writer."""
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="badges"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
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
        on_delete=models.SET_NULL
    )

    class Meta:
        unique_together = ("writer", "badge", "issued_at")
        ordering = ["-issued_at"]

    def __str__(self):
        return f"{self.writer} → {self.badge.name} ({'Revoked' if self.revoked else 'Active'})"
    
