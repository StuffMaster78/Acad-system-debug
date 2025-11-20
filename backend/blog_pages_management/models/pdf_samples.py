"""
PDF Sample/Download models for blog posts.
Allows readers to download sample PDFs attached to blog posts.
"""
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.conf import settings

User = get_user_model()


class PDFSampleSection(models.Model):
    """
    Sections within blog posts that contain downloadable PDF samples.
    Supports multiple PDFs per section for different sample types.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='pdf_sample_sections'
    )
    title = models.CharField(
        max_length=255,
        help_text="Section title (e.g., 'Download Sample', 'Case Studies')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what these samples contain"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying sections within the blog"
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
        verbose_name = "PDF Sample Section"
        verbose_name_plural = "PDF Sample Sections"
        indexes = [
            models.Index(fields=['blog', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.blog.title}"


class PDFSample(models.Model):
    """
    Individual PDF file that can be downloaded from a PDF sample section.
    """
    section = models.ForeignKey(
        PDFSampleSection,
        on_delete=models.CASCADE,
        related_name='pdf_samples'
    )
    title = models.CharField(
        max_length=255,
        help_text="Display name for this PDF (e.g., 'Sample Report 2024')"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of what this PDF contains"
    )
    pdf_file = models.FileField(
        upload_to='blog_pdf_samples/%Y/%m/',
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
        related_name='uploaded_pdf_samples'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['is_featured', 'display_order', 'title']
        verbose_name = "PDF Sample"
        verbose_name_plural = "PDF Samples"
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


class PDFSampleDownload(models.Model):
    """
    Tracks PDF downloads for analytics and access control.
    """
    pdf_sample = models.ForeignKey(
        PDFSample,
        on_delete=models.CASCADE,
        related_name='downloads'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pdf_downloads'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the downloader"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent"
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Session ID for tracking"
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = "PDF Sample Download"
        verbose_name_plural = "PDF Sample Downloads"
        indexes = [
            models.Index(fields=['pdf_sample', 'downloaded_at']),
            models.Index(fields=['user', 'downloaded_at']),
        ]
    
    def __str__(self):
        user_str = self.user.username if self.user else self.ip_address or "Anonymous"
        return f"{self.pdf_sample.title} - {user_str} - {self.downloaded_at}"

