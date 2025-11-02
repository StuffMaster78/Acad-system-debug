"""
Enhanced draft and editing models for blog posts and service pages.
Includes auto-save, revisions, preview, and collaborative editing features.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class BlogPostRevision(models.Model):
    """
    Full revision/snapshot of a blog post at a point in time.
    Allows restoring to previous versions and viewing diffs.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='revisions'
    )
    revision_number = models.PositiveIntegerField(
        help_text="Sequential revision number"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    # Store serialized versions of related objects
    authors_data = JSONField(
        default=list,
        blank=True,
        help_text="List of author IDs at time of revision"
    )
    tags_data = JSONField(
        default=list,
        blank=True,
        help_text="List of tag IDs at time of revision"
    )
    category_id = models.PositiveIntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_revisions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(
        blank=True,
        help_text="Summary of changes in this revision"
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Whether this is the current published version"
    )
    
    # Revision comments and notes
    revision_notes = models.TextField(
        blank=True,
        help_text="Notes or comments about this revision"
    )
    revision_tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Tags for categorizing revisions (e.g., 'major-update', 'typo-fix')"
    )
    
    class Meta:
        ordering = ['-revision_number']
        unique_together = ['blog', 'revision_number']
        indexes = [
            models.Index(fields=['blog', 'is_current']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.blog.title} - Revision {self.revision_number}"


class BlogPostAutoSave(models.Model):
    """
    Auto-saved drafts of blog posts.
    Automatically saves work-in-progress content periodically.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='autosaves'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    authors_data = JSONField(default=list, blank=True)
    tags_data = JSONField(default=list, blank=True)
    category_id = models.PositiveIntegerField(null=True, blank=True)
    
    saved_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_autosaves'
    )
    saved_at = models.DateTimeField(auto_now_add=True)
    is_recovered = models.BooleanField(
        default=False,
        help_text="Whether this autosave was recovered/used"
    )
    
    class Meta:
        ordering = ['-saved_at']
        indexes = [
            models.Index(fields=['blog', 'saved_at']),
            models.Index(fields=['saved_by', 'saved_at']),
        ]
    
    def __str__(self):
        return f"Autosave for {self.blog.title} at {self.saved_at}"


class BlogPostEditLock(models.Model):
    """
    Prevents concurrent editing by locking blog posts during editing sessions.
    """
    blog = models.OneToOneField(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='edit_lock'
    )
    locked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_edit_locks'
    )
    locked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When the lock expires (default: 30 minutes)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the lock is currently active"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['blog', 'is_active', 'expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Set expiration time on save."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if the lock has expired."""
        return timezone.now() > self.expires_at
    
    def extend_lock(self, minutes=30):
        """Extend the lock duration."""
        self.expires_at = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save(update_fields=['expires_at'])
    
    def release_lock(self):
        """Release the edit lock."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def __str__(self):
        status = "Active" if self.is_active and not self.is_expired() else "Expired"
        return f"{self.blog.title} - Locked by {self.locked_by.username} ({status})"


class BlogPostPreview(models.Model):
    """
    Preview tokens for viewing unpublished/draft blog posts.
    Allows sharing preview links without publishing.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='previews'
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Unique preview token"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_previews'
    )
    expires_at = models.DateTimeField(
        help_text="When the preview link expires"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the preview link is active"
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times preview was viewed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['token', 'is_active', 'expires_at']),
        ]
    
    def is_expired(self):
        """Check if preview token has expired."""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if preview token is valid (active and not expired)."""
        return self.is_active and not self.is_expired()
    
    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def __str__(self):
        return f"Preview for {self.blog.title} - Token: {self.token[:8]}..."


class ServicePageRevision(models.Model):
    """Full revision/snapshot of a service page."""
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='revisions'
    )
    revision_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    header = models.CharField(max_length=255)
    content = models.TextField()
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_page_revisions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    change_summary = models.TextField(blank=True)
    is_current = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-revision_number']
        unique_together = ['service_page', 'revision_number']
    
    def __str__(self):
        return f"{self.service_page.title} - Revision {self.revision_number}"


class ServicePageAutoSave(models.Model):
    """Auto-saved drafts of service pages."""
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='autosaves'
    )
    title = models.CharField(max_length=255)
    header = models.CharField(max_length=255)
    content = models.TextField()
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    
    saved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    is_recovered = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"Autosave for {self.service_page.title} at {self.saved_at}"


class ServicePageEditLock(models.Model):
    """Edit locks for service pages."""
    service_page = models.OneToOneField(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='edit_lock'
    )
    locked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    locked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def release_lock(self):
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def __str__(self):
        return f"{self.service_page.title} - Locked by {self.locked_by.username}"


class ServicePagePreview(models.Model):
    """Preview tokens for service pages."""
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='previews'
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        return self.is_active and not self.is_expired()
    
    def __str__(self):
        return f"Preview for {self.service_page.title} - Token: {self.token[:8]}..."

