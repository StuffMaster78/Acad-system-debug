"""
Serializers for editor usage tracking.
"""
from rest_framework import serializers
from ..models.editor_usage_tracking import (
    EditorSession,
    EditorAction,
    EditorProductivityMetrics
)


class EditorSessionSerializer(serializers.ModelSerializer):
    """Serializer for editor sessions."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    content_title = serializers.SerializerMethodField()
    duration_minutes = serializers.FloatField(read_only=True)
    
    class Meta:
        model = EditorSession
        fields = [
            'id', 'user', 'user_username', 'website', 'website_name',
            'content_type', 'content_id', 'content_title',
            'session_start', 'session_end', 'is_active',
            'total_keystrokes', 'total_actions',
            'characters_added', 'characters_removed',
            'templates_used', 'snippets_used', 'blocks_used',
            'health_checks_run', 'auto_saves_count', 'manual_saves_count',
            'duration_minutes'
        ]
        read_only_fields = [
            'session_start', 'session_end', 'is_active',
            'total_keystrokes', 'total_actions',
            'characters_added', 'characters_removed',
            'templates_used', 'snippets_used', 'blocks_used',
            'health_checks_run', 'auto_saves_count', 'manual_saves_count',
            'duration_minutes'
        ]
    
    def get_content_title(self, obj):
        """Get title of content being edited."""
        try:
            content = obj.content_object
            if hasattr(content, 'title'):
                return content.title
            return f"{obj.content_type} #{obj.content_id}"
        except:
            return f"{obj.content_type} #{obj.content_id}"


class EditorActionSerializer(serializers.ModelSerializer):
    """Serializer for editor actions."""
    session_user = serializers.CharField(source='session.user.username', read_only=True)
    
    class Meta:
        model = EditorAction
        fields = [
            'id', 'session', 'session_user', 'action_type',
            'timestamp', 'metadata'
        ]
        read_only_fields = ['timestamp']


class EditorProductivityMetricsSerializer(serializers.ModelSerializer):
    """Serializer for productivity metrics."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = EditorProductivityMetrics
        fields = [
            'id', 'user', 'user_username', 'website', 'website_name',
            'period_start', 'period_end',
            'total_sessions', 'average_session_duration', 'longest_session',
            'total_keystrokes', 'average_keystrokes_per_session',
            'total_characters_written',
            'templates_used_count', 'snippets_used_count', 'blocks_used_count',
            'health_checks_count',
            'words_per_minute', 'content_quality_score',
            'productivity_score', 'calculated_at'
        ]
        read_only_fields = ['calculated_at']

