"""
Approval workflow models for blog posts and service pages.
Enables draft → review → approved → published workflow.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

User = get_user_model()


class BlogPostWorkflow(models.Model):
    """
    Tracks approval workflow state for blog posts.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted for Review'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
    ]
    
    blog = models.OneToOneField(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='workflow'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_submissions',
        help_text="User who submitted for review"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    assigned_reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_blog_reviews',
        help_text="Reviewer assigned to review this post"
    )
    review_started_at = models.DateTimeField(null=True, blank=True)
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_blogs',
        help_text="User who approved the post"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rejected_blogs',
        help_text="User who rejected the post"
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection"
    )
    
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='published_blogs',
        help_text="User who published the post"
    )
    published_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'assigned_reviewer']),
            models.Index(fields=['submitted_at']),
        ]
    
    def __str__(self):
        return f"{self.blog.title} - {self.get_status_display()}"


class BlogPostReviewComment(models.Model):
    """
    Comments and feedback during the review process.
    """
    workflow = models.ForeignKey(
        BlogPostWorkflow,
        on_delete=models.CASCADE,
        related_name='review_comments'
    )
    commenter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_review_comments'
    )
    comment = models.TextField(
        help_text="Review comment or feedback"
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether the comment has been addressed"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_blog_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Highlight specific content
    highlighted_text = models.TextField(
        blank=True,
        help_text="Specific text being commented on"
    )
    content_metadata = JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata (e.g., field name, position)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['workflow', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.workflow.blog.title}"


class WorkflowTransition(models.Model):
    """
    Audit trail for workflow status transitions.
    """
    workflow = models.ForeignKey(
        BlogPostWorkflow,
        on_delete=models.CASCADE,
        related_name='transitions'
    )
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    transitioned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_workflow_transitions'
    )
    transition_reason = models.TextField(
        blank=True,
        help_text="Reason for the status change"
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        help_text="Additional transition metadata"
    )
    transitioned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-transitioned_at']
        indexes = [
            models.Index(fields=['workflow', 'transitioned_at']),
        ]
    
    def __str__(self):
        return f"{self.workflow.blog.title}: {self.from_status} → {self.to_status}"


class ContentTemplate(models.Model):
    """
    Reusable content templates for blog posts and service pages.
    """
    TEMPLATE_TYPE_CHOICES = [
        ('blog_post', 'Blog Post'),
        ('service_page', 'Service Page'),
        ('section', 'Content Section'),
        ('cta', 'CTA Block'),
    ]
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='content_templates'
    )
    name = models.CharField(
        max_length=255,
        help_text="Template name"
    )
    description = models.TextField(
        blank=True,
        help_text="Template description"
    )
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        db_index=True
    )
    
    # Template content
    title_template = models.CharField(
        max_length=255,
        blank=True,
        help_text="Title template (supports variables like {{title}})"
    )
    content_template = models.TextField(
        blank=True,
        help_text="Content template"
    )
    meta_title_template = models.CharField(
        max_length=255,
        blank=True
    )
    meta_description_template = models.TextField(
        blank=True
    )
    
    # Default values
    default_values = JSONField(
        default=dict,
        blank=True,
        help_text="Default values for template variables"
    )
    
    # Template metadata
    category = models.ForeignKey(
        'blog_pages_management.BlogCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(
        'blog_pages_management.BlogTag',
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether template is active"
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times template has been used"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        indexes = [
            models.Index(fields=['website', 'template_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ContentSnippet(models.Model):
    """
    Reusable content snippets for quick insertion.
    """
    SNIPPET_TYPE_CHOICES = [
        ('text', 'Text'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
        ('code', 'Code Block'),
        ('table', 'Table'),
        ('list', 'List'),
    ]
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='content_snippets'
    )
    name = models.CharField(
        max_length=255,
        help_text="Snippet name"
    )
    description = models.TextField(
        blank=True,
        help_text="Snippet description"
    )
    snippet_type = models.CharField(
        max_length=20,
        choices=SNIPPET_TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(
        help_text="Snippet content"
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for easy searching"
    )
    
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='content_snippets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['website', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_snippet_type_display()})"
    
    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

