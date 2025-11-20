"""
PDF Sample/Download models for service pages.
Allows readers to download sample PDFs attached to service pages.
"""
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()


class ServicePagePDFSampleSection(models.Model):
    """
    Sections within service pages that contain downloadable PDF samples.
    """
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='pdf_sample_sections'
    )
    title = models.CharField(
        max_length=255,
        help_text="Section title (e.g., 'Download Samples', 'Resources')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what these samples contain"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying sections within the service page"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this section is visible"
    )
    requires_auth = models.BooleanField(
        default=False,
        help_text="Require user authentication to download"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = "Service Page PDF Sample Section"
        verbose_name_plural = "Service Page PDF Sample Sections"
        indexes = [
            models.Index(fields=['service_page', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.service_page.title}"


class ServicePagePDFSample(models.Model):
    """
    Individual PDF file that can be downloaded from a service page PDF sample section.
    """
    section = models.ForeignKey(
        ServicePagePDFSampleSection,
        on_delete=models.CASCADE,
        related_name='pdf_samples'
    )
    title = models.CharField(
        max_length=255,
        help_text="Display name for this PDF"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of what this PDF contains"
    )
    pdf_file = models.FileField(
        upload_to='service_pages_pdf_samples/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="PDF file to upload (max 10MB)"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes (auto-calculated)"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying PDFs within the section"
    )
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this PDF has been downloaded"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured PDFs appear first"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this PDF is available for download"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_service_pdf_samples'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['is_featured', 'display_order', 'title']
        verbose_name = "Service Page PDF Sample"
        verbose_name_plural = "Service Page PDF Samples"
        indexes = [
            models.Index(fields=['section', 'is_active']),
            models.Index(fields=['download_count']),
        ]
    
    def save(self, *args, **kwargs):
        """Calculate file size on save."""
        if self.pdf_file and not self.file_size:
            try:
                self.file_size = self.pdf_file.size
            except (AttributeError, OSError):
                pass
        super().save(*args, **kwargs)
    
    def increment_download(self):
        """Increment download counter."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    @property
    def file_size_human(self):
        """Return human-readable file size."""
        if not self.file_size:
            return "Unknown"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def __str__(self):
        return f"{self.title} - {self.section.title}"


class ServicePagePDFSampleDownload(models.Model):
    """
    Tracks PDF downloads for service pages analytics and access control.
    """
    pdf_sample = models.ForeignKey(
        ServicePagePDFSample,
        on_delete=models.CASCADE,
        related_name='downloads'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_pdf_downloads'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = "Service Page PDF Sample Download"
        verbose_name_plural = "Service Page PDF Sample Downloads"
        indexes = [
            models.Index(fields=['pdf_sample', 'downloaded_at']),
            models.Index(fields=['user', 'downloaded_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else self.ip_address or "Anonymous"
        return f"{self.pdf_sample.title} - {user_str} - {self.downloaded_at}"

