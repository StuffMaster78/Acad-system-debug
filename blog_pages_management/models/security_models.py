"""
Security and rate limiting models for preview tokens and other features.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class PreviewTokenRateLimit(models.Model):
    """
    Rate limiting for preview tokens.
    """
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True
    )
    view_count = models.PositiveIntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    blocked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Token blocked until this time"
    )
    is_blocked = models.BooleanField(
        default=False,
        help_text="Whether token is currently blocked"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['token', 'is_blocked']),
        ]
    
    def __str__(self):
        return f"Rate limit for {self.token[:16]}..."
    
    @classmethod
    def check_rate_limit(cls, token: str, max_views: int = 100, time_window_hours: int = 24) -> bool:
        """
        Check if token has exceeded rate limit.
        
        Args:
            token: Preview token
            max_views: Maximum views allowed
            time_window_hours: Time window in hours
        
        Returns:
            True if within limit, False if exceeded
        """
        rate_limit, created = cls.objects.get_or_create(token=token)
        
        # Check if blocked
        if rate_limit.is_blocked and rate_limit.blocked_until:
            if timezone.now() < rate_limit.blocked_until:
                return False
            else:
                # Unblock if time expired
                rate_limit.is_blocked = False
                rate_limit.blocked_until = None
                rate_limit.view_count = 0
                rate_limit.save()
        
        # Check if in time window
        if rate_limit.last_viewed_at:
            time_since_last_view = timezone.now() - rate_limit.last_viewed_at
            if time_since_last_view > timedelta(hours=time_window_hours):
                # Reset counter if outside time window
                rate_limit.view_count = 0
                rate_limit.last_viewed_at = timezone.now()
                rate_limit.save()
        
        # Check limit
        if rate_limit.view_count >= max_views:
            rate_limit.is_blocked = True
            rate_limit.blocked_until = timezone.now() + timedelta(hours=time_window_hours)
            rate_limit.save()
            return False
        
        return True
    
    @classmethod
    def increment_view(cls, token: str):
        """Increment view count for token."""
        rate_limit, created = cls.objects.get_or_create(token=token)
        rate_limit.view_count += 1
        rate_limit.last_viewed_at = timezone.now()
        rate_limit.save()


class AuditTrail(models.Model):
    """
    Comprehensive audit trail for all content changes.
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('publish', 'Published'),
        ('unpublish', 'Unpublished'),
        ('archive', 'Archived'),
        ('restore', 'Restored'),
        ('submit', 'Submitted for Review'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('lock', 'Locked'),
        ('unlock', 'Unlocked'),
    ]
    
    # Generic relation to any content object
    content_type = models.CharField(
        max_length=100,
        help_text="Type of content (e.g., 'blog_post', 'service_page')"
    )
    content_id = models.PositiveIntegerField(
        help_text="ID of the content object"
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_trails'
    )
    
    # Change details
    field_changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Fields that were changed: {field_name: {'old': ..., 'new': ...}}"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata about the action"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text="User agent string"
    )
    
    performed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['action', 'performed_at']),
            models.Index(fields=['performed_by', 'performed_at']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.content_type} #{self.content_id} by {self.performed_by}"
    
    @classmethod
    def log_action(
        cls,
        content_type: str,
        content_id: int,
        action: str,
        user,
        field_changes: dict = None,
        metadata: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """
        Log an action to the audit trail.
        
        Args:
            content_type: Type of content (e.g., 'blog_post')
            content_id: ID of the content object
            action: Action performed
            user: User performing the action
            field_changes: Dict of field changes
            metadata: Additional metadata
            ip_address: IP address of user
            user_agent: User agent string
        """
        return cls.objects.create(
            content_type=content_type,
            content_id=content_id,
            action=action,
            performed_by=user,
            field_changes=field_changes or {},
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

