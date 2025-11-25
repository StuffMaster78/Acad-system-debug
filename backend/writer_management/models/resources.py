"""
Models for writer resources and guides.
Admins can upload guides and share resources for writers' personal development.
"""
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website

User = settings.AUTH_USER_MODEL


class WriterResourceCategory(models.Model):
    """
    Categories for organizing writer resources (e.g., "Writing Tips", "Style Guides", "Tools").
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_resource_categories"
    )
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., 'Writing Tips', 'Style Guides')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of the category"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which categories are displayed"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        unique_together = ['website', 'name']
        verbose_name_plural = "Writer Resource Categories"
    
    def __str__(self):
        return f"{self.name} ({self.website.name})"


class WriterResource(models.Model):
    """
    Resources and guides for writers' personal development.
    Admins can upload documents, share links, and provide educational content.
    """
    RESOURCE_TYPE_CHOICES = [
        ('document', 'Document (PDF, DOC, etc.)'),
        ('link', 'External Link'),
        ('video', 'Video'),
        ('article', 'Article/Guide'),
        ('tool', 'Tool/Software'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_resources"
    )
    category = models.ForeignKey(
        WriterResourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources"
    )
    title = models.CharField(
        max_length=255,
        help_text="Resource title"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the resource"
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        default='document'
    )
    
    # For document uploads
    file = models.FileField(
        upload_to='writer_resources/',
        blank=True,
        null=True,
        help_text="Upload a document (PDF, DOC, etc.)"
    )
    
    # For external links
    external_url = models.URLField(
        blank=True,
        null=True,
        help_text="External link URL"
    )
    
    # For video embeds
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Video URL (YouTube, Vimeo, etc.)"
    )
    
    # For articles/guides (rich text content)
    content = models.TextField(
        blank=True,
        null=True,
        help_text="Article/guide content (HTML supported)"
    )
    
    # Metadata
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Feature this resource prominently"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which resources are displayed"
    )
    
    # Tracking
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this resource has been viewed"
    )
    download_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this resource has been downloaded"
    )
    
    # Admin tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_writer_resources",
        limit_choices_to={'role__in': ['admin', 'superadmin']}
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_writer_resources",
        limit_choices_to={'role__in': ['admin', 'superadmin']}
    )
    
    class Meta:
        ordering = ['display_order', '-created_at']
        indexes = [
            models.Index(fields=['website', 'is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    def get_url(self):
        """Get the appropriate URL based on resource type."""
        if self.resource_type == 'link' and self.external_url:
            return self.external_url
        elif self.resource_type == 'video' and self.video_url:
            return self.video_url
        elif self.resource_type == 'document' and self.file:
            return self.file.url
        return None
    
    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download(self):
        """Increment download count."""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class WriterResourceView(models.Model):
    """
    Track which writers have viewed which resources.
    """
    resource = models.ForeignKey(
        WriterResource,
        on_delete=models.CASCADE,
        related_name="views"
    )
    writer = models.ForeignKey(
        'writer_management.WriterProfile',
        on_delete=models.CASCADE,
        related_name="resource_views"
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['resource', 'writer']
        indexes = [
            models.Index(fields=['writer', 'viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.writer.user.username} viewed {self.resource.title}"

