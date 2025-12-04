"""
Editor usage tracking models for detailed editor analytics.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class EditorSession(models.Model):
    """
    Tracks an editor session - from opening editor to closing.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='editor_sessions'
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='editor_sessions'
    )
    
    # Content being edited
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'content_id')
    
    # Session tracking
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Usage metrics
    total_keystrokes = models.PositiveIntegerField(default=0)
    total_actions = models.PositiveIntegerField(default=0)
    characters_added = models.PositiveIntegerField(default=0)
    characters_removed = models.PositiveIntegerField(default=0)
    
    # Tool usage
    templates_used = models.PositiveIntegerField(default=0)
    snippets_used = models.PositiveIntegerField(default=0)
    blocks_used = models.PositiveIntegerField(default=0)
    health_checks_run = models.PositiveIntegerField(default=0)
    
    # Productivity
    auto_saves_count = models.PositiveIntegerField(default=0)
    manual_saves_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-session_start']
        indexes = [
            models.Index(fields=['user', 'session_start']),
            models.Index(fields=['website', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.content_type} #{self.content_id} - {self.session_start}"
    
    def end_session(self):
        """End the editing session."""
        self.session_end = timezone.now()
        self.is_active = False
        self.save()
    
    @property
    def duration_minutes(self):
        """Get session duration in minutes."""
        if not self.session_end:
            end = timezone.now()
        else:
            end = self.session_end
        delta = end - self.session_start
        return delta.total_seconds() / 60


class EditorAction(models.Model):
    """
    Tracks individual editor actions for detailed analytics.
    """
    ACTION_TYPES = [
        ('keystroke', 'Keystroke'),
        ('format', 'Format Change'),
        ('insert', 'Content Insert'),
        ('delete', 'Content Delete'),
        ('template_use', 'Template Used'),
        ('snippet_use', 'Snippet Used'),
        ('block_use', 'Block Used'),
        ('health_check', 'Health Check'),
        ('save', 'Save'),
        ('auto_save', 'Auto Save'),
        ('undo', 'Undo'),
        ('redo', 'Redo'),
        ('copy', 'Copy'),
        ('paste', 'Paste'),
    ]
    
    session = models.ForeignKey(
        EditorSession,
        on_delete=models.CASCADE,
        related_name='actions'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Action metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional action data (e.g., format type, content length)"
    )
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.session.user.username} - {self.action_type} - {self.timestamp}"


class EditorProductivityMetrics(models.Model):
    """
    Aggregated productivity metrics per user/website.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='productivity_metrics'
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='productivity_metrics'
    )
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Session metrics
    total_sessions = models.PositiveIntegerField(default=0)
    average_session_duration = models.FloatField(
        default=0,
        help_text="Average session duration in minutes"
    )
    longest_session = models.FloatField(
        default=0,
        help_text="Longest session in minutes"
    )
    
    # Activity metrics
    total_keystrokes = models.PositiveIntegerField(default=0)
    average_keystrokes_per_session = models.FloatField(default=0)
    total_characters_written = models.PositiveIntegerField(default=0)
    
    # Tool usage
    templates_used_count = models.PositiveIntegerField(default=0)
    snippets_used_count = models.PositiveIntegerField(default=0)
    blocks_used_count = models.PositiveIntegerField(default=0)
    health_checks_count = models.PositiveIntegerField(default=0)
    
    # Efficiency metrics
    words_per_minute = models.FloatField(
        default=0,
        help_text="Average words per minute"
    )
    content_quality_score = models.FloatField(
        default=0,
        help_text="Average content health score"
    )
    
    # Productivity score (0-100)
    productivity_score = models.FloatField(
        default=0,
        help_text="Overall productivity score"
    )
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'website', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['user', 'period_start']),
            models.Index(fields=['website', 'productivity_score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.website.name} - {self.period_start} to {self.period_end}"

