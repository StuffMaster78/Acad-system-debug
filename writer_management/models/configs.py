from django.db import models
from websites.models import Website


class WriterConfig(models.Model):
    """
    Admin-controlled settings for writers.
    This allows admins to enable/disable order takes.
    """
    website = models.ForeignKey(
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
    max_takes_per_order = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of writers that can take a single order."
    )

    def __str__(self):
        return f"Config for {self.website.name} - Takes Enabled: {self.takes_enabled}"

    class Meta:
        verbose_name = "Writer Config"
        verbose_name_plural = "Writer Configs"
        unique_together = ("website",)
        ordering = ["-id"]

class WriterConfigAdmin(models.Model):
    """
    Admin interface for managing writer configurations.
    Allows admins to create, update, and delete configurations.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    takes_enabled = models.BooleanField(
        default=True,
        help_text="If True, writers can take orders. If False, writers must request orders."
    )
    max_requests_per_writer = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of order requests a writer can have at once."
    )
    max_takes_per_writer = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of orders a writer can take at once."
    )
    max_takes_per_order = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of writers that can take a single order."
    )

    def __str__(self):
        return f"Admin Config for {self.website.name} - Takes Enabled: {self.takes_enabled}"
    
    class Meta:
        verbose_name = "Writer Config Admin"
        verbose_name_plural = "Writer Config Admins"
        unique_together = ("website",)
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        """
        Ensure only one config per website.
        """
        if WriterConfig.objects.filter(website=self.website).exists():
            raise ValueError("A configuration for this website already exists.")
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
        'auth.User', on_delete=models.SET_NULL, null=True,
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