"""
Serializers for analytics models.
"""
from rest_framework import serializers
from ..models.analytics_models import (
    EditorAnalytics, BlogPostAnalytics, ContentPerformanceMetrics
)


class EditorAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for editor analytics."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = EditorAnalytics
        fields = [
            'id', 'user', 'user_username', 'website', 'website_name',
            'total_posts_created', 'total_posts_published', 'total_drafts',
            'average_time_to_publish', 'average_edit_time', 'total_editing_time',
            'average_revision_count', 'posts_requiring_revision',
            'total_clicks', 'total_conversions',
            'average_clicks_per_post', 'average_conversions_per_post',
            'on_time_publish_rate', 'first_draft_approval_rate',
            'last_calculated_at'
        ]
        read_only_fields = ['last_calculated_at']


class BlogPostAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for blog post analytics."""
    blog_title = serializers.CharField(source='blog.title', read_only=True)
    
    class Meta:
        model = BlogPostAnalytics
        fields = [
            'id', 'blog', 'blog_title',
            'draft_creation_date', 'time_to_first_edit', 'time_in_draft', 'time_in_review',
            'total_edits', 'total_revisions', 'total_autosaves', 'last_edited_at',
            'submission_count', 'approval_count', 'rejection_count',
            'publish_delay', 'was_on_time',
            'clicks_day_1', 'clicks_week_1', 'clicks_month_1',
            'conversions_day_1', 'conversions_week_1', 'conversions_month_1',
            'click_velocity', 'conversion_rate',
            'last_calculated_at'
        ]
        read_only_fields = ['last_calculated_at']


class ContentPerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer for content performance metrics."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = ContentPerformanceMetrics
        fields = [
            'id', 'website', 'website_name', 'period_start', 'period_end',
            'total_posts_created', 'total_posts_published', 'total_drafts',
            'average_posts_per_day', 'average_draft_completion_rate',
            'average_time_to_publish', 'abandoned_drafts',
            'average_revisions_per_post', 'average_edits_per_post',
            'total_clicks', 'total_conversions',
            'average_clicks_per_post', 'average_conversions_per_post',
            'top_performing_post_id', 'most_prolific_editor_id',
            'total_editors_active', 'calculated_at'
        ]
        read_only_fields = ['calculated_at']

