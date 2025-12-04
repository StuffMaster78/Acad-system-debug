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


class WebsiteContentMetrics(models.Model):
    """
    Aggregated content metrics per website, broken down by category and tag.
    Designed for powering the CMS \"metrics\" section.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="website_content_metrics",
    )
    calculated_at = models.DateTimeField(auto_now_add=True)

    # Overall counts
    total_posts = models.PositiveIntegerField(default=0)
    published_posts = models.PositiveIntegerField(default=0)
    draft_posts = models.PositiveIntegerField(default=0)

    # Category and tag breakdowns stored as JSON for flexibility:
    # {
    #   "Category Name": {
    #       "post_count": 10,
    #       "view_count": 1200,
    #       "conversion_count": 45
    #   },
    #   ...
    # }
    category_metrics = models.JSONField(default=dict, blank=True)

    # {
    #   "tag-slug-or-name": {
    #       "post_count": 5,
    #       "view_count": 400,
    #       "conversion_count": 12
    #   },
    #   ...
    # }
    tag_metrics = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-calculated_at"]
        indexes = [
            models.Index(fields=["website", "calculated_at"]),
        ]

    def __str__(self) -> str:
        return f"Website metrics for {self.website.name} at {self.calculated_at}"

    @classmethod
    def calculate_for_website(cls, website):
        """
        Calculate a fresh metrics snapshot for a given website.

        Uses BlogPost, BlogCategory, BlogTag and cached engagement fields
        (view_count, conversion_count) where available.
        """
        from ..models import BlogPost, BlogCategory, BlogTag

        posts = BlogPost.objects.filter(website=website, is_deleted=False)

        total_posts = posts.count()
        published_posts = posts.filter(is_published=True).count()
        draft_posts = posts.filter(status="draft").count()

        # Category metrics
        category_metrics = {}
        categories = BlogCategory.objects.filter(website=website, is_active=True)
        for category in categories:
            cat_posts = posts.filter(category=category)
            if not cat_posts.exists():
                continue

            category_metrics[category.name] = {
                "post_count": cat_posts.count(),
                "view_count": cat_posts.aggregate(
                    total_views=Sum("view_count")
                )["total_views"]
                or 0,
                "conversion_count": cat_posts.aggregate(
                    total_conversions=Sum("conversion_count")
                )["total_conversions"]
                or 0,
            }

        # Tag metrics
        tag_metrics = {}
        tags = BlogTag.objects.filter(website=website)
        for tag in tags:
            tag_posts = posts.filter(tags=tag)
            if not tag_posts.exists():
                continue

            key = tag.name
            tag_metrics[key] = {
                "post_count": tag_posts.count(),
                "view_count": tag_posts.aggregate(
                    total_views=Sum("view_count")
                )["total_views"]
                or 0,
                "conversion_count": tag_posts.aggregate(
                    total_conversions=Sum("conversion_count")
                )["total_conversions"]
                or 0,
            }

        metrics = cls.objects.create(
            website=website,
            total_posts=total_posts,
            published_posts=published_posts,
            draft_posts=draft_posts,
            category_metrics=category_metrics,
            tag_metrics=tag_metrics,
        )
        return metrics


class WebsitePublishingTarget(models.Model):
    """
    Monthly publishing targets for each website.
    Admins can set targets, or system can estimate based on research.
    """
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='publishing_target',
        help_text="Website this target applies to"
    )
    monthly_target = models.PositiveIntegerField(
        default=4,
        help_text="Target number of blog posts to publish per month"
    )
    is_auto_estimated = models.BooleanField(
        default=True,
        help_text="Whether target was auto-estimated or manually set by admin"
    )
    estimation_reason = models.TextField(
        blank=True,
        help_text="Reason for the estimated target (e.g., 'Based on industry average')"
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_publishing_targets'
    )
    # Customizable reminder threshold (in months)
    freshness_threshold_months = models.PositiveIntegerField(
        default=3,
        help_text="Number of months before content is considered stale"
    )
    
    class Meta:
        verbose_name = "Website Publishing Target"
        verbose_name_plural = "Website Publishing Targets"
    
    def __str__(self):
        return f"{self.website.name}: {self.monthly_target} posts/month"
    
    @classmethod
    def get_or_create_for_website(cls, website):
        """Get or create publishing target for a website."""
        target, created = cls.objects.get_or_create(
            website=website,
            defaults={
                'monthly_target': cls.estimate_target_for_website(website),
                'is_auto_estimated': True,
                'estimation_reason': 'Auto-estimated based on website age and industry average'
            }
        )
        return target
    
    @classmethod
    def estimate_target_for_website(cls, website):
        """
        Estimate monthly publishing target based on:
        - Website age
        - Industry average (4-8 posts/month for content marketing)
        - Historical publishing rate if available
        """
        from ..models import BlogPost
        from datetime import timedelta
        
        # Get historical publishing rate
        three_months_ago = timezone.now() - timedelta(days=90)
        recent_posts = BlogPost.objects.filter(
            website=website,
            is_published=True,
            publish_date__gte=three_months_ago
        ).count()
        
        # Average per month over last 3 months
        historical_rate = recent_posts / 3 if recent_posts > 0 else 0
        
        # Base target: 4-6 posts/month (industry average for content marketing)
        base_target = 4
        
        # Adjust based on historical rate
        if historical_rate > 0:
            # Use historical rate, but cap at reasonable max (12/month)
            estimated = min(max(int(historical_rate), 2), 12)
        else:
            # New website or no history: start with base target
            estimated = base_target
        
        return estimated
    
    def get_current_month_stats(self):
        """Get publishing stats for current month."""
        from ..models import BlogPost
        from datetime import datetime
        
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        published_this_month = BlogPost.objects.filter(
            website=self.website,
            is_published=True,
            publish_date__gte=month_start
        ).count()
        
        return {
            'target': self.monthly_target,
            'published': published_this_month,
            'remaining': max(0, self.monthly_target - published_this_month),
            'percentage': (published_this_month / self.monthly_target * 100) if self.monthly_target > 0 else 0,
            'month': now.strftime('%B %Y')
        }


class CategoryPublishingTarget(models.Model):
    """
    Per-category monthly publishing targets.
    Allows setting different targets for different content categories.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='category_publishing_targets',
        help_text="Website this target applies to"
    )
    category = models.ForeignKey(
        'blog_pages_management.BlogCategory',
        on_delete=models.CASCADE,
        related_name='publishing_targets',
        help_text="Category this target applies to"
    )
    monthly_target = models.PositiveIntegerField(
        default=1,
        help_text="Target number of posts in this category per month"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this target is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['website', 'category']
        verbose_name = "Category Publishing Target"
        verbose_name_plural = "Category Publishing Targets"
    
    def __str__(self):
        return f"{self.website.name} - {self.category.name}: {self.monthly_target}/month"
    
    def get_current_month_stats(self):
        """Get publishing stats for current month for this category."""
        from ..models import BlogPost
        
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        published_this_month = BlogPost.objects.filter(
            website=self.website,
            category=self.category,
            is_published=True,
            publish_date__gte=month_start
        ).count()
        
        return {
            'target': self.monthly_target,
            'published': published_this_month,
            'remaining': max(0, self.monthly_target - published_this_month),
            'percentage': (published_this_month / self.monthly_target * 100) if self.monthly_target > 0 else 0,
            'month': now.strftime('%B %Y')
        }


class ContentFreshnessReminder(models.Model):
    """
    Tracks content that needs updating (not updated in X months).
    Used to send reminders to admins/superadmins.
    """
    blog_post = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='freshness_reminders',
        help_text="Blog post that needs updating"
    )
    last_reminder_sent = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last reminder was sent"
    )
    reminder_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of reminders sent for this content"
    )
    is_acknowledged = models.BooleanField(
        default=False,
        help_text="Admin has acknowledged this reminder"
    )
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_freshness_reminders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Content Freshness Reminder"
        verbose_name_plural = "Content Freshness Reminders"
        indexes = [
            models.Index(fields=['blog_post', 'is_acknowledged']),
        ]
    
    def __str__(self):
        return f"Freshness reminder for: {self.blog_post.title}"
    
    @classmethod
    def get_stale_content(cls, months_threshold=None, website=None):
        """
        Get all published blog posts that haven't been updated in X months.
        If months_threshold is None, uses website's custom threshold.
        """
        from ..models import BlogPost
        from datetime import timedelta
        
        # Get threshold from website settings if not provided
        if months_threshold is None:
            if website:
                try:
                    target = WebsitePublishingTarget.objects.get(website=website)
                    months_threshold = target.freshness_threshold_months
                except WebsitePublishingTarget.DoesNotExist:
                    months_threshold = 3  # Default
            else:
                months_threshold = 3  # Default
        
        threshold_date = timezone.now() - timedelta(days=months_threshold * 30)
        
        queryset = BlogPost.objects.filter(
            is_published=True,
            is_deleted=False,
            updated_at__lt=threshold_date
        )
        
        if website:
            queryset = queryset.filter(website=website)
        
        return queryset.select_related('website', 'category').prefetch_related('tags', 'authors')
    
    @classmethod
    def create_or_update_reminders(cls, months_threshold=None, website=None):
        """
        Create or update freshness reminders for stale content.
        Returns list of reminders created/updated.
        """
        stale_posts = cls.get_stale_content(months_threshold, website)
        reminders = []
        
        for post in stale_posts:
            reminder, created = cls.objects.get_or_create(
                blog_post=post,
                defaults={'reminder_count': 0}
            )
            reminders.append(reminder)
        
        return reminders

