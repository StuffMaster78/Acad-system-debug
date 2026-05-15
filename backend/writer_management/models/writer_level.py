"""
WriterLevel defines the hierarchical tier structure for writers.

It does NOT contain pricing or business logic.

It only defines:
- identity of the level
- ordering in hierarchy
- relationship to settings
- basic visibility constraints
"""

from django.db import models


class WriterLevel(models.Model):
    """
    Represents a writer tier in the system.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_levels",
    )

    name = models.CharField(
        max_length=50,
        help_text="Human-readable level name (e.g. Expert)",
    )

    description = models.TextField(
        blank=True,
        default="",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower = higher rank in hierarchy",
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_default = models.BooleanField(
        default=False,
        help_text="Fallback level for new writers",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Writer Level"
        verbose_name_plural = "Writer Levels"
        ordering = ["display_order", "name"]
        unique_together = [["website", "name"]]

    def __str__(self) -> str:
        return f"{self.name} (level {self.display_order})"

    @property
    def settings_safe(self):
        """
        Safe accessor for settings.
        Avoids None crashes in services.
        """
        return getattr(self, "settings", None)