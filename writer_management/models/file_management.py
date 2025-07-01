from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order


class WriterFileDownloadLog(models.Model):
    """
    Logs when a writer downloads order files.
    Helps with tracking and accountability.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_download_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_download_logs"
    )
    file_name = models.CharField(
        max_length=255, help_text="Name of the downloaded file."
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Download: {self.writer.user.username} - {self.file_name} ({self.downloaded_at})"
    
    class Meta:
        verbose_name = "Writer File Download Log"
        verbose_name_plural = "Writer File Download Logs"
        ordering = ['-downloaded_at']
    
class WriterFileUploadLog(models.Model):
    """
    Logs when a writer uploads files for an order.
    Helps with tracking and accountability.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_upload_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_upload_logs"
    )
    file_name = models.CharField(
        max_length=255, help_text="Name of the uploaded file."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Upload: {self.writer.user.username} - {self.file_name} ({self.uploaded_at})"
    

    class Meta:
        verbose_name = "Writer File Upload Log"
        verbose_name_plural = "Writer File Upload Logs"
        ordering = ['-uploaded_at']
    

class WriterFileAccessLog(models.Model):
    """
    Logs when a writer accesses files related to an order.
    Helps with tracking file access for security and accountability.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_access_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_access_logs"
    )
    file_name = models.CharField(
        max_length=255, help_text="Name of the accessed file."
    )
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Access: {self.writer.user.username} - {self.file_name} ({self.accessed_at})"
    
    class Meta:
        verbose_name = "Writer File Access Log"
        verbose_name_plural = "Writer File Access Logs"
        ordering = ['-accessed_at']
    

class WriterFileDeletionLog(models.Model):
    """
    Logs when a writer deletes files related to an order.
    Helps with tracking file deletions for accountability.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_deletion_logs"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_deletion_logs"
    )
    file_name = models.CharField(
        max_length=255, help_text="Name of the deleted file."
    )
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Deletion: {self.writer.user.username} - {self.file_name} ({self.deleted_at})"
    
    class Meta:
        verbose_name = "Writer File Deletion Log"
        verbose_name_plural = "Writer File Deletion Logs"
        ordering = ['-deleted_at']
    

class WriterFileVersion(models.Model):
    """
    Tracks different versions of files uploaded by writers.
    Useful for maintaining file history and version control.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_versions"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_versions"
    )
    file_name = models.CharField(
        max_length=255, help_text="Name of the file."
    )
    version_number = models.IntegerField(
        help_text="Version number of the file."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Version: {self.writer.user.username} - {self.file_name} (Version {self.version_number})"
    
    class Meta:
        unique_together = ('website', 'writer', 'order', 'file_name', 'version_number')
        verbose_name = "Writer File Version"
        verbose_name_plural = "Writer File Versions"
        ordering = ['-uploaded_at']
    

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
    

class WriterFileAccessHistory(models.Model):
    """
    Tracks the history of file access by writers.
    Useful for auditing and tracking file access history.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="file_access_history"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="writer_file_access_history"
    )
    file_name = models.CharField(
        max_length=255, help_text="Name of the accessed file."
    )
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File Access History: {self.writer.user.username} - {self.file_name} ({self.accessed_at})"
    
    class Meta:
        verbose_name = "Writer File Access History"
        verbose_name_plural = "Writer File Access Histories"
        ordering = ['-accessed_at']