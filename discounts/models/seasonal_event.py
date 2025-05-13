from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class SeasonalEvent(models.Model):
    """
    Represents a seasonal event that discounts can be associated with.
    Examples: Summer, Black Friday, CyberMonday etc.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='seasonal_event'
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Event name (e.g., Black Friday, Christmas Sale)"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the event"
    )
     # Active window
    start_date = models.DateTimeField(help_text="When the event starts")
    end_date = models.DateTimeField(help_text="When the event ends")
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this event is currently active"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def clean(self):
        """Ensure end date is after start date."""
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")
        if self.end_date < timezone.now():
            self.is_active = False

    def __str__(self):
        return f"{self.name} ({self.start_date.date()} - {self.end_date.date()})"