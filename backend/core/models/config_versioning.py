"""
Generic Configuration Versioning System

Tracks changes to all configuration models for audit and rollback purposes.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.db.models import JSONField
from django.utils import timezone


class ConfigVersion(models.Model):
    """
    Generic model to track versions of any configuration object.
    Uses ContentType to support any model type.
    """
    # Generic foreign key to any config model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    config_object = GenericForeignKey('content_type', 'object_id')
    
    # Version metadata
    version_number = models.PositiveIntegerField(
        help_text="Sequential version number for this config"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this version was created"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="config_versions_created",
        help_text="User who created this version"
    )
    
    # Snapshot of config data
    config_data = JSONField(
        help_text="Complete snapshot of configuration at this version"
    )
    
    # Change tracking
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('updated', 'Updated'),
            ('deleted', 'Deleted'),
            ('restored', 'Restored'),
        ],
        default='updated',
        help_text="Type of change that created this version"
    )
    change_summary = models.TextField(
        blank=True,
        null=True,
        help_text="Summary of what changed in this version"
    )
    changed_fields = JSONField(
        default=list,
        blank=True,
        help_text="List of field names that were changed"
    )
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_versions',
        help_text="Previous version (for version chain)"
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this version"
    )
    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is the current active version"
    )
    
    class Meta:
        verbose_name = "Configuration Version"
        verbose_name_plural = "Configuration Versions"
        ordering = ['-version_number', '-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['content_type', 'object_id', 'version_number']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [['content_type', 'object_id', 'version_number']]
    
    def __str__(self):
        config_name = f"{self.content_type.model} #{self.object_id}"
        return f"Version {self.version_number} of {config_name} ({self.change_type})"
    
    @classmethod
    def get_next_version_number(cls, content_type, object_id):
        """Get the next version number for a config object."""
        last_version = cls.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-version_number').first()
        
        if last_version:
            return last_version.version_number + 1
        return 1
    
    @classmethod
    def get_current_version(cls, content_type, object_id):
        """Get the current version for a config object."""
        return cls.objects.filter(
            content_type=content_type,
            object_id=object_id,
            is_current=True
        ).first()
    
    @classmethod
    def get_version_history(cls, content_type, object_id, limit=None):
        """Get version history for a config object."""
        queryset = cls.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-version_number')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset

