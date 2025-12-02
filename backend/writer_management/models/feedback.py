"""
Feedback Loop Models
Structured feedback from editors to writers and from clients to writers/editors.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from websites.models import Website


class Feedback(models.Model):
    """
    Base feedback model for structured feedback between users.
    """
    FEEDBACK_TYPE_CHOICES = [
        ('editor_to_writer', 'Editor to Writer'),
        ('client_to_writer', 'Client to Writer'),
        ('client_to_editor', 'Client to Editor'),
        ('writer_to_client', 'Writer to Client'),
    ]
    
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    
    # Feedback relationship
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks_given'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks_received'
    )
    
    # Structured feedback
    overall_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        help_text="Overall rating (1-5)"
    )
    
    # Category ratings
    quality_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True
    )
    communication_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True
    )
    timeliness_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True
    )
    professionalism_rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True
    )
    
    # Written feedback
    strengths = models.TextField(
        blank=True,
        help_text="What went well / strengths"
    )
    areas_for_improvement = models.TextField(
        blank=True,
        help_text="Areas that need improvement"
    )
    specific_feedback = models.TextField(
        blank=True,
        help_text="Specific, actionable feedback"
    )
    
    # Structured feedback points
    feedback_points = models.JSONField(
        default=list,
        blank=True,
        help_text="List of specific feedback points: [{'section': 'Introduction', 'issue': '...', 'suggestion': '...'}]"
    )
    
    # Visibility
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this feedback is visible to others (for portfolios)"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether feedback is anonymous"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'feedback_type']),
            models.Index(fields=['to_user', 'feedback_type']),
            models.Index(fields=['from_user', 'created_at']),
        ]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
    
    def __str__(self):
        return f"Feedback from {self.from_user.email} to {self.to_user.email} - Order #{self.order.id}"


class FeedbackHistory(models.Model):
    """
    Aggregated feedback history per user.
    Used for analytics and portfolio display.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedback_history'
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='feedback_histories'
    )
    
    # Aggregated metrics
    total_feedbacks = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )
    average_quality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    average_communication_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    average_timeliness_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Breakdown by type
    editor_feedbacks_count = models.PositiveIntegerField(default=0)
    client_feedbacks_count = models.PositiveIntegerField(default=0)
    
    # Time-based metrics
    last_30_days_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    last_90_days_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Last updated
    last_calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'website')
        indexes = [
            models.Index(fields=['user', 'website']),
            models.Index(fields=['average_rating']),
        ]
        verbose_name = "Feedback History"
        verbose_name_plural = "Feedback Histories"
    
    def __str__(self):
        return f"Feedback History for {self.user.email} - Avg: {self.average_rating}"
    
    def recalculate(self):
        """Recalculate aggregated metrics from Feedback objects."""
        from django.db.models import Avg, Count, Q
        from writer_management.models.feedback import Feedback
        
        feedbacks = Feedback.objects.filter(
            to_user=self.user,
            website=self.website
        )
        
        self.total_feedbacks = feedbacks.count()
        
        if self.total_feedbacks > 0:
            self.average_rating = feedbacks.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
            self.average_quality_rating = feedbacks.aggregate(Avg('quality_rating'))['quality_rating__avg']
            self.average_communication_rating = feedbacks.aggregate(Avg('communication_rating'))['communication_rating__avg']
            self.average_timeliness_rating = feedbacks.aggregate(Avg('timeliness_rating'))['timeliness_rating__avg']
            
            self.editor_feedbacks_count = feedbacks.filter(feedback_type='editor_to_writer').count()
            self.client_feedbacks_count = feedbacks.filter(feedback_type='client_to_writer').count()
            
            # Time-based
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            ninety_days_ago = timezone.now() - timezone.timedelta(days=90)
            
            recent_30 = feedbacks.filter(created_at__gte=thirty_days_ago)
            recent_90 = feedbacks.filter(created_at__gte=ninety_days_ago)
            
            self.last_30_days_rating = recent_30.aggregate(Avg('overall_rating'))['overall_rating__avg']
            self.last_90_days_rating = recent_90.aggregate(Avg('overall_rating'))['overall_rating__avg']
        
        self.save()

