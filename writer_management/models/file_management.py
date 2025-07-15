from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order


class WriterFile(models.Model):
    """
    Represents versioned files uploaded by writers.
    Each upload is a new version. Supports audit, soft delete, and lifecycle states.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="files"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_files"
    )
    file = models.FileField(upload_to='writer_files/')
    file_name = models.CharField(
        max_length=255, help_text="Name of the uploaded file."
    )
    file_type = models.CharField(
        max_length=100, blank=True, help_text="MIME type of the uploaded file."
    )
    file_size = models.PositiveIntegerField(
        help_text="Size of the file in bytes."
    )

    version_number = models.PositiveIntegerField(
        help_text="Auto-incremented version number of the file."
    )

    description = models.TextField(
        blank=True, help_text="Description of the file."
    )
    is_public = models.BooleanField(
        default=False, help_text="If True, the file is accessible publicly."
    )
    is_deleted = models.BooleanField(
        default=False, help_text="If True, the file is marked as deleted."
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    last_accessed = models.DateTimeField(null=True, blank=True)
    last_accessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="last_accessed_files"
    )

    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="last_modified_files"
    )

    is_archived = models.BooleanField(default=False)
    archive_date = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(blank=True)

    is_locked = models.BooleanField(default=False)
    lock_reason = models.TextField(blank=True)
    lock_date = models.DateTimeField(null=True, blank=True)
    lock_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="locked_files"
    )
    lock_until = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writer File"
        verbose_name_plural = "Writer Files"
        ordering = ['-uploaded_at']
        unique_together = ("website", "writer", "order", "file_name", "version_number")

    def __str__(self):
        return f"{self.writer.user.username} - {self.file_name} (v{self.version_number})"

    def save(self, *args, **kwargs):
        if not self.version_number:
            last_version = WriterFile.objects.filter(
                website=self.website,
                writer=self.writer,
                order=self.order,
                file_name=self.file_name
            ).aggregate(models.Max('version_number'))['version_number__max'] or 0
            self.version_number = last_version + 1
        super().save(*args, **kwargs)


class WriterFileActivityLog(models.Model):
    ACTION_CHOICES = [
        ("download", "Download"),
        ("upload", "Upload"),
        ("access", "Access"),
        ("delete", "Delete"),
    ]

    website = models.ForeignKey(
        Website, on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE, related_name="file_activity_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="writer_file_activity_logs"
    )
    file_name = models.CharField(max_length=255)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']
        verbose_name = "Writer File Activity Log"
        verbose_name_plural = "Writer File Activity Logs"

    def __str__(self):
        return f"{self.writer.user.username} {self.action} {self.file_name} ({self.occurred_at})"
class WriterFileAccessRequest(models.Model):
    """
    Tracks requests made by writers to access files.
    Useful for auditing and tracking file access requests.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_access_requests"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_access_requests"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Denied", "Denied")],
        default="Pending", help_text="Status of the access request."
    )

    def __str__(self):
        return f"File Access Request: {self.writer.user.username} for Order {self.order.id} ({self.status})"
    
    class Meta:
        verbose_name = "Writer File Access Request"
        verbose_name_plural = "Writer File Access Requests"
        ordering = ['-requested_at']


