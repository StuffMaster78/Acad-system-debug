"""
Collaborative editing models for real-time collaboration.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import JSONField

User = get_user_model()


class CollaborativeSession(models.Model):
    """
    Tracks a collaborative editing session.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'content_id')
    
    session_id = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique session identifier"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaborative_sessions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['content_type', 'content_id', 'is_active']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.content_type} #{self.content_id}"


class CollaborativeEditor(models.Model):
    """
    Tracks editors in a collaborative session.
    """
    session = models.ForeignKey(
        CollaborativeSession,
        on_delete=models.CASCADE,
        related_name='editors'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaborative_edits'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    cursor_position = models.PositiveIntegerField(
        default=0,
        help_text="Current cursor position in content"
    )
    selection_start = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Selection start position"
    )
    selection_end = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Selection end position"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['session', 'user']
        indexes = [
            models.Index(fields=['session', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} in session {self.session.session_id}"


class CollaborativeChange(models.Model):
    """
    Tracks changes in a collaborative editing session.
    """
    CHANGE_TYPES = [
        ('insert', 'Insert'),
        ('delete', 'Delete'),
        ('format', 'Format'),
        ('cursor', 'Cursor Move'),
    ]
    
    session = models.ForeignKey(
        CollaborativeSession,
        on_delete=models.CASCADE,
        related_name='changes'
    )
    editor = models.ForeignKey(
        CollaborativeEditor,
        on_delete=models.CASCADE,
        related_name='changes'
    )
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    position = models.PositiveIntegerField(
        help_text="Position in content where change occurred"
    )
    length = models.PositiveIntegerField(
        default=0,
        help_text="Length of change (for delete/format)"
    )
    content = models.TextField(
        blank=True,
        help_text="Content inserted or changed"
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        help_text="Additional change metadata (formatting, etc.)"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    applied = models.BooleanField(
        default=False,
        help_text="Whether change has been applied to content"
    )
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['applied', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.change_type} at {self.position} by {self.editor.user.username}"


class CollaborativePresence(models.Model):
    """
    Tracks real-time presence of editors.
    """
    session = models.ForeignKey(
        CollaborativeSession,
        on_delete=models.CASCADE,
        related_name='presence'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaborative_presence'
    )
    last_heartbeat = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['session', 'user']
        indexes = [
            models.Index(fields=['session', 'is_online']),
            models.Index(fields=['last_heartbeat']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

