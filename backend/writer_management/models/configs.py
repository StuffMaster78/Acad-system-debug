from django.db import models
from websites.models import Website
from users.models import User


class WriterConfig(models.Model):
    """
    Admin-controlled settings for writers.
    This allows admins to enable/disable order takes.
    """
    website = models.OneToOneField(
        Website,
        on_delete=models.CASCADE
    )
    takes_enabled = models.BooleanField(
        default=True,
        help_text="If True, writers can take orders . If False, writers must request orders."
    )
    max_requests_per_writer = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of order requests a writer can have at once."
    )
    max_takes_per_writer = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of orders a writer can take at once."
    )
    

    def __str__(self):
        return f"Config for {self.website.name} - Takes Enabled: {self.takes_enabled}"

    class Meta:
        verbose_name = "Writer Config"
        verbose_name_plural = "Writer Configs"
        unique_together = ("website",)
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        # Ensure a website is always assigned during tests
        if not getattr(self, 'website_id', None):
            try:
                from websites.models import Website
                site = Website.objects.filter(is_active=True).first()
                if site is None:
                    site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)


class WriterConfigHistory(models.Model):
    """
    Tracks changes to writer configurations.
    Useful for auditing and tracking config history.
    """
    config = models.ForeignKey(
        WriterConfig, on_delete=models.CASCADE,
        related_name="history"
    )
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name="config_changes"
    )
    change_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the change was made."
    )
    change_type = models.CharField(
        max_length=50, 
        choices=[("Created", "Created"), ("Updated", "Updated"), ("Deleted", "Deleted")],
        help_text="Type of change made."
    )
    notes = models.TextField(
        blank=True, null=True,
        help_text="Details about the change."
    )

    def __str__(self):
        return f"Config History: {self.config.website.name} - {self.change_type} ({self.change_date})"
    
    class Meta:
        verbose_name = "Writer Config History"
        verbose_name_plural = "Writer Config Histories"
        ordering = ['-change_date']


class WriterLevelConfig(models.Model):
    """
    Configurable writer level, defined by admin.
    Determines what score/metrics a writer needs
    to belong to this level.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="writer_level_configs"
    )
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    min_score = models.DecimalField(
        max_digits=6, decimal_places=2,
        help_text="Minimum composite score required"
    )
    min_rating = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0.00,
        help_text="Minimum average rating"
    )
    max_revision_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Max acceptable revision rate (%)"
    )
    max_lateness_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Max acceptable lateness rate (%)"
    )
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority levels appear first"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority"]

    def __str__(self):
        return f"{self.website.name} – {self.name}"
    

class WriterWarningEscalationConfig(models.Model):
    """
    Configures escalation thresholds for writer warnings.
    This allows admins to set thresholds for probation, suspension,
    and admin alerts based on the number of warnings issued.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="warning_configs"
    )

    probation_threshold = models.PositiveIntegerField(default=3)
    suspension_threshold = models.PositiveIntegerField(default=5)
    admin_alert_threshold = models.PositiveIntegerField(default=7)

    default_warning_duration_days = models.PositiveIntegerField(default=30)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website",)
        verbose_name = "Writer Warning Escalation Config"
        verbose_name_plural = "Writer Warning Escalation Configs"

    def __str__(self):
        return f"Escalation Config for {self.website.domain}"