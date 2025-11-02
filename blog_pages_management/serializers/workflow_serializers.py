"""
Serializers for workflow, templates, and related models.
"""
from rest_framework import serializers
from ..models.workflow_models import (
    BlogPostWorkflow, BlogPostReviewComment, WorkflowTransition,
    ContentTemplate, ContentSnippet
)


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for workflow transitions."""
    transitioned_by_username = serializers.CharField(source='transitioned_by.username', read_only=True)
    
    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'workflow', 'from_status', 'to_status',
            'transitioned_by', 'transitioned_by_username',
            'transition_reason', 'metadata', 'transitioned_at'
        ]
        read_only_fields = ['transitioned_at']


class BlogPostReviewCommentSerializer(serializers.ModelSerializer):
    """Serializer for review comments."""
    commenter_username = serializers.CharField(source='commenter.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = BlogPostReviewComment
        fields = [
            'id', 'workflow', 'commenter', 'commenter_username',
            'comment', 'is_resolved', 'resolved_by', 'resolved_by_username',
            'resolved_at', 'highlighted_text', 'content_metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'resolved_at']


class BlogPostWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for blog post workflows."""
    blog_title = serializers.CharField(source='blog.title', read_only=True)
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True)
    assigned_reviewer_username = serializers.CharField(source='assigned_reviewer.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    rejected_by_username = serializers.CharField(source='rejected_by.username', read_only=True)
    published_by_username = serializers.CharField(source='published_by.username', read_only=True)
    
    review_comments = BlogPostReviewCommentSerializer(many=True, read_only=True)
    transitions = WorkflowTransitionSerializer(many=True, read_only=True)
    unresolved_comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPostWorkflow
        fields = [
            'id', 'blog', 'blog_title', 'status',
            'submitted_by', 'submitted_by_username', 'submitted_at',
            'assigned_reviewer', 'assigned_reviewer_username', 'review_started_at',
            'approved_by', 'approved_by_username', 'approved_at',
            'rejected_by', 'rejected_by_username', 'rejected_at', 'rejection_reason',
            'published_by', 'published_by_username', 'published_at',
            'review_comments', 'transitions', 'unresolved_comments_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_unresolved_comments_count(self, obj):
        """Get count of unresolved comments."""
        return obj.review_comments.filter(is_resolved=False).count()


class ContentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for content templates."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentTemplate
        fields = [
            'id', 'website', 'name', 'description', 'template_type',
            'title_template', 'content_template', 'meta_title_template',
            'meta_description_template', 'default_values',
            'category', 'category_name', 'tags', 'tags_count',
            'is_active', 'usage_count', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['usage_count', 'created_at', 'updated_at']
    
    def get_tags_count(self, obj):
        """Get count of tags."""
        return obj.tags.count()


class ContentSnippetSerializer(serializers.ModelSerializer):
    """Serializer for content snippets."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ContentSnippet
        fields = [
            'id', 'website', 'name', 'description', 'snippet_type',
            'content', 'tags', 'is_active', 'usage_count',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['usage_count', 'created_at', 'updated_at']

