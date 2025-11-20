# writer_management.models.status.py

from django.db import models
from websites.models import Website
from writer_management.models.profile import WriterProfile

class WriterStatus(models.Model):
    """
    Centralized status model for each writer.
    Reflects current active state based on strikes,
    suspensions, blacklists, etc.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE
    )
    writer = models.OneToOneField(
        WriterProfile, on_delete=models.CASCADE, related_name="status"
    )

    is_active = models.BooleanField(
        default=True, help_text="Is the writer allowed to access orders?")
    is_suspended = models.BooleanField(
        default=False, help_text="Is the writer currently suspended?")
    is_blacklisted = models.BooleanField(
        default=False, help_text="Is the writer currently blacklisted?")
    is_on_probation = models.BooleanField(
        default=False,
        help_text="Is the writer currently on probation?"
    )
    strikes = models.PositiveIntegerField(default=0)
    
    active_strikes = models.PositiveIntegerField(default=0)
    last_strike_at = models.DateTimeField(null=True, blank=True)
    suspension_ends_at = models.DateTimeField(null=True, blank=True)
    probation_ends_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "writer")
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["is_blacklisted"]),
            models.Index(fields=["is_suspended"]),
        ]

    def __str__(self):
        return f"{self.writer.user.username} | Active: {self.is_active}"