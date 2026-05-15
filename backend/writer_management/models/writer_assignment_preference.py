"""
Soft routing preferences for assignment matching.

These preferences are NOT hard eligibility rules.
They are signals used by the routing engine to improve
assignment quality and writer satisfaction.

Routing may still assign outside these preferences
when necessary.
"""

from django.db import models


class WriterAssignmentPreference(models.Model):
    """
    Soft assignment routing preferences.

    Used by:
    - AssignmentRoutingService
    - SmartMatchingService
    """

    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="assignment_preferences",
    )

    preferred_subjects = models.ManyToManyField(
        "order_configs.Subject",
        blank=True,
        related_name="preferred_writers",
    )

    preferred_types_of_work = models.ManyToManyField(
        "order_configs.TypeOfWork",
        blank=True,
        related_name="preferred_writers",
    )

    preferred_academic_levels = models.ManyToManyField(
        "order_configs.AcademicLevel",
        blank=True,
        related_name="preferred_writers",
    )

    preferred_citation_styles = models.ManyToManyField(
        "order_configs.CitationStyle",
        blank=True,
        related_name="preferred_writers",
    )

    accepts_urgent_orders = models.BooleanField(
        default=True,
    )

    accepts_weekend_orders = models.BooleanField(
        default=True,
    )

    accepts_night_orders = models.BooleanField(
        default=True,
    )

    preferred_min_deadline_hours = models.PositiveIntegerField(
        default=12,
        help_text=(
            "Preferred minimum time before deadline."
        ),
    )

    auto_accept_orders = models.BooleanField(
        default=False,
    )

    auto_accept_preferred_only = models.BooleanField(
        default=True,
    )

    notes = models.TextField(
        blank=True,
        default="",
        help_text="Internal routing notes.",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Writer Assignment Preference"
        verbose_name_plural = "Writer Assignment Preferences"

    def __str__(self) -> str:
        return f"AssignmentPreference<{self.writer.id}>"