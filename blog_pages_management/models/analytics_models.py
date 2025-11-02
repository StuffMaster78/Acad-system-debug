"""
Advanced analytics models for blog content management.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class EditorAnalytics(models.Model):
    """
    Analytics for individual editors/authors.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='editor_analytics'
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='editor_analytics'
    )
    
    # Publishing stats
    total_posts_created = models.PositiveIntegerField(default=0)
    total_posts_published = models.PositiveIntegerField(default=0)
    total_drafts = models.PositiveIntegerField(default=0)
    
    # Time metrics
    average_time_to_publish = models.FloatField(
        null=True,
        blank=True,
        help_text="Average time from draft creation to publish (in hours)"
    )
    average_edit_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Average time spent editing (in hours)"
    )
    total_editing_time = models.FloatField(
        default=0,
        help_text="Total time spent editing (in hours)"
    )
    
    # Quality metrics
    average_revision_count = models.FloatField(
        default=0,
        help_text="Average number of revisions per post"
    )
    posts_requiring_revision = models.PositiveIntegerField(
        default=0,
        help_text="Number of posts that required revisions before approval"
    )
    
    # Engagement metrics
    total_clicks = models.PositiveIntegerField(default=0)
    total_conversions = models.PositiveIntegerField(default=0)
    average_clicks_per_post = models.FloatField(default=0)
    average_conversions_per_post = models.FloatField(default=0)
    
    # Performance metrics
    on_time_publish_rate = models.FloatField(
        default=0,
        help_text="Percentage of posts published on time"
    )
    first_draft_approval_rate = models.FloatField(
        default=0,
        help_text="Percentage of posts approved on first submission"
    )
    
    # Last updated
    last_calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'website']
        indexes = [
            models.Index(fields=['website', 'total_posts_published']),
            models.Index(fields=['average_clicks_per_post']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.website.name}"
    
    @classmethod
    def calculate_for_user(cls, user, website):
        """Calculate analytics for a user."""
        from ..models import BlogPost
        from ..models.draft_editing import BlogPostRevision
        
        analytics, created = cls.objects.get_or_create(
            user=user,
            website=website
        )
        
        # Get user's posts
        posts = BlogPost.objects.filter(
            website=website,
            authors=user
        )
        
        # Publishing stats
        analytics.total_posts_created = posts.count()
        analytics.total_posts_published = posts.filter(
            status='published',
            is_published=True
        ).count()
        analytics.total_drafts = posts.filter(
            status='draft'
        ).count()
        
        # Calculate average time to publish
        published_posts = posts.filter(
            status='published',
            publish_date__isnull=False
        )
        if published_posts.exists():
            total_hours = 0
            count = 0
            for post in published_posts:
                if post.created_at and post.publish_date:
                    delta = post.publish_date - post.created_at
                    total_hours += delta.total_seconds() / 3600
                    count += 1
            if count > 0:
                analytics.average_time_to_publish = total_hours / count
        
        # Calculate average revision count
        revision_counts = []
        for post in posts:
            revision_count = BlogPostRevision.objects.filter(
                blog=post
            ).count()
            revision_counts.append(revision_count)
        
        if revision_counts:
            analytics.average_revision_count = sum(revision_counts) / len(revision_counts)
        
        # Engagement metrics
        published_by_user = posts.filter(status='published')
        if published_by_user.exists():
            analytics.total_clicks = sum(p.click_count for p in published_by_user)
            analytics.total_conversions = sum(p.conversion_count for p in published_by_user)
            analytics.average_clicks_per_post = analytics.total_clicks / published_by_user.count()
            analytics.average_conversions_per_post = analytics.total_conversions / published_by_user.count()
        
        analytics.save()
        return analytics


class BlogPostAnalytics(models.Model):
    """
    Advanced analytics for individual blog posts.
    """
    blog = models.OneToOneField(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='advanced_analytics'
    )
    
    # Draft metrics
    draft_creation_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the draft was first created"
    )
    time_to_first_edit = models.FloatField(
        null=True,
        blank=True,
        help_text="Time from creation to first edit (in hours)"
    )
    time_in_draft = models.FloatField(
        null=True,
        blank=True,
        help_text="Total time spent in draft status (in hours)"
    )
    time_in_review = models.FloatField(
        null=True,
        blank=True,
        help_text="Total time spent in review (in hours)"
    )
    
    # Edit metrics
    total_edits = models.PositiveIntegerField(default=0)
    total_revisions = models.PositiveIntegerField(default=0)
    total_autosaves = models.PositiveIntegerField(default=0)
    last_edited_at = models.DateTimeField(null=True, blank=True)
    
    # Workflow metrics
    submission_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times submitted for review"
    )
    approval_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times approved"
    )
    rejection_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times rejected"
    )
    
    # Performance metrics
    publish_delay = models.FloatField(
        null=True,
        blank=True,
        help_text="Delay from scheduled time to actual publish (in hours)"
    )
    was_on_time = models.BooleanField(
        default=True,
        help_text="Whether published on scheduled time"
    )
    
    # Engagement trajectory
    clicks_day_1 = models.PositiveIntegerField(default=0)
    clicks_week_1 = models.PositiveIntegerField(default=0)
    clicks_month_1 = models.PositiveIntegerField(default=0)
    conversions_day_1 = models.PositiveIntegerField(default=0)
    conversions_week_1 = models.PositiveIntegerField(default=0)
    conversions_month_1 = models.PositiveIntegerField(default=0)
    
    # Calculated metrics
    click_velocity = models.FloatField(
        default=0,
        help_text="Clicks per day"
    )
    conversion_rate = models.FloatField(
        default=0,
        help_text="Conversion rate (conversions/clicks)"
    )
    
    # Last updated
    last_calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['time_in_draft']),
            models.Index(fields=['total_edits']),
            models.Index(fields=['click_velocity']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.blog.title}"
    
    @classmethod
    def calculate_for_blog(cls, blog):
        """Calculate analytics for a blog post."""
        from ..models.draft_editing import BlogPostRevision, BlogPostAutoSave
        
        analytics, created = cls.objects.get_or_create(blog=blog)
        
        # Draft metrics
        if blog.created_at:
            analytics.draft_creation_date = blog.created_at
            
            if blog.status == 'published' and blog.publish_date:
                delta = blog.publish_date - blog.created_at
                analytics.time_in_draft = delta.total_seconds() / 3600
        
        # Edit metrics
        analytics.total_revisions = BlogPostRevision.objects.filter(
            blog=blog
        ).count()
        analytics.total_autosaves = BlogPostAutoSave.objects.filter(
            blog=blog
        ).count()
        
        # Workflow metrics
        from ..models.workflow_models import BlogPostWorkflow
        try:
            workflow = blog.workflow
            analytics.submission_count = WorkflowTransition.objects.filter(
                workflow=workflow,
                to_status='submitted'
            ).count()
            analytics.approval_count = WorkflowTransition.objects.filter(
                workflow=workflow,
                to_status='approved'
            ).count()
            analytics.rejection_count = WorkflowTransition.objects.filter(
                workflow=workflow,
                to_status='rejected'
            ).count()
            
            if workflow.review_started_at and workflow.approved_at:
                delta = workflow.approved_at - workflow.review_started_at
                analytics.time_in_review = delta.total_seconds() / 3600
        except BlogPostWorkflow.DoesNotExist:
            pass
        
        # Engagement trajectory
        if blog.publish_date:
            now = timezone.now()
            day_1 = blog.publish_date + timedelta(days=1)
            week_1 = blog.publish_date + timedelta(days=7)
            month_1 = blog.publish_date + timedelta(days=30)
            
            # This would need actual click tracking per time period
            # For now, we'll calculate from current metrics
            days_since_publish = (now - blog.publish_date).days
            if days_since_publish > 0:
                analytics.click_velocity = blog.click_count / days_since_publish
                if blog.click_count > 0:
                    analytics.conversion_rate = blog.conversion_count / blog.click_count
        
        # Performance metrics
        if blog.status == 'scheduled' and blog.scheduled_publish_date:
            if blog.publish_date:
                delta = blog.publish_date - blog.scheduled_publish_date
                analytics.publish_delay = delta.total_seconds() / 3600
                analytics.was_on_time = abs(analytics.publish_delay) < 1  # Within 1 hour
        
        analytics.save()
        return analytics


class ContentPerformanceMetrics(models.Model):
    """
    Aggregated performance metrics for content.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='content_metrics'
    )
    period_start = models.DateField(
        help_text="Start of the reporting period"
    )
    period_end = models.DateField(
        help_text="End of the reporting period"
    )
    
    # Publishing metrics
    total_posts_created = models.PositiveIntegerField(default=0)
    total_posts_published = models.PositiveIntegerField(default=0)
    total_drafts = models.PositiveIntegerField(default=0)
    average_posts_per_day = models.FloatField(default=0)
    
    # Draft metrics
    average_draft_completion_rate = models.FloatField(
        default=0,
        help_text="Percentage of drafts that become published"
    )
    average_time_to_publish = models.FloatField(default=0)
    abandoned_drafts = models.PositiveIntegerField(
        default=0,
        help_text="Drafts older than 30 days never published"
    )
    
    # Editing metrics
    average_revisions_per_post = models.FloatField(default=0)
    average_edits_per_post = models.FloatField(default=0)
    
    # Engagement metrics
    total_clicks = models.PositiveIntegerField(default=0)
    total_conversions = models.PositiveIntegerField(default=0)
    average_clicks_per_post = models.FloatField(default=0)
    average_conversions_per_post = models.FloatField(default=0)
    top_performing_post_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Editor metrics
    most_prolific_editor_id = models.PositiveIntegerField(null=True, blank=True)
    total_editors_active = models.PositiveIntegerField(default=0)
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['website', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['website', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.website.name} - {self.period_start} to {self.period_end}"

