import uuid

from django.conf import settings
from django.db import models

class FileQuota(models.Model):
    """Per-tenant storage quotas."""

    site = models.OneToOneField(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="file_quota",
    )
    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="file_quota",
    )

    # Limits
    max_total_size_bytes = models.BigIntegerField(
        default=10_737_418_240, # 10 GB
        help_text="Total storage quota in bytes (default: 10GB)",
    )
    max_file_size_bytes = models.BigIntegerField(
        default=104_857_600, # 100 MB
        help_text="Max single file in bytes (default: 100MB)",
    )
    max_files_count = models.PositiveIntegerField(
        default=10_000,
        help_text="Maximum number of files per tenant",
    )

    # Current usage (refreshed by nightly Celery task)
    current_size_bytes = models.BigIntegerField(default=0)
    current_files_count = models.PositiveIntegerField(default=0)

    # Alert threshold
    warning_threshold_percent = models.PositiveIntegerField(
        default=80,
        help_text="Alert when usage exceeds this percentage",
    )
    last_calculated = models.DateTimeField(auto_now=True)


    @property
    def usage_percent(self):
        if not self.max_total_size_bytes:
            return 0
        return (self.current_size_bytes / self.max_total_size_bytes) * 100

    @property
    def is_over_quota(self):
        return self.current_size_bytes >= self.max_total_size_bytes

    @property
    def is_near_quota(self):
        return self.usage_percent >= self.warning_threshold_percent

    @property
    def remaining_bytes(self):
        return max(0, self.max_total_size_bytes - self.current_size_bytes)


    def __str__(self):
        pct = self.usage_percent
        return f"{self.website}: {pct:.1f}% used"
