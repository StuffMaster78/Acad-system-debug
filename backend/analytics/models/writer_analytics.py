"""
Writer Analytics Models
Effective hourly rate, earnings vs time, revision/approval rates, quality scores.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Avg, Count
# Use string references to avoid circular imports


class WriterAnalytics(models.Model):
    """
    Aggregated analytics for writers.
    """
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='writer_analytics',
        limit_choices_to={'role': 'writer'}
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='writer_analytics'
    )
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Earnings metrics
    total_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total earnings in period"
    )
    average_order_earnings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Average earnings per order"
    )
    
    # Time metrics
    total_hours_worked = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Total hours worked (estimated from orders)"
    )
    effective_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Effective hourly rate (earnings / hours)"
    )
    
    # Order metrics
    total_orders_completed = models.PositiveIntegerField(default=0)
    total_orders_in_progress = models.PositiveIntegerField(default=0)
    average_completion_time_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Average time to complete order"
    )
    
    # Revision metrics
    total_revisions = models.PositiveIntegerField(default=0)
    revision_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders requiring revisions"
    )
    average_revisions_per_order = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    
    # Approval metrics
    approval_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders approved without revision"
    )
    rejection_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders rejected"
    )
    
    # Quality metrics
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating from feedback"
    )
    quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Calculated quality score"
    )
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('writer', 'website', 'period_start', 'period_end')
        indexes = [
            models.Index(fields=['writer', 'website', 'period_start']),
        ]
        verbose_name = "Writer Analytics"
        verbose_name_plural = "Writer Analytics"
    
    def __str__(self):
        return f"Analytics for {self.writer.email} - {self.period_start} to {self.period_end}"
    
    def recalculate(self):
        """Recalculate all metrics from orders and feedback."""
        orders = Order.objects.filter(
            writer=self.writer,
            website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end
        )
        
        # Earnings
        completed_orders = orders.filter(status='completed')
        self.total_orders_completed = completed_orders.count()
        self.total_orders_in_progress = orders.filter(status='in_progress').count()
        
        # Calculate earnings from writer payments
        from writer_management.models.payout import WriterPayment
        payments = WriterPayment.objects.filter(
            writer=self.writer,
            website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end,
            status='completed'
        )
        self.total_earnings = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        
        if self.total_orders_completed > 0:
            self.average_order_earnings = self.total_earnings / self.total_orders_completed
        
        # Time metrics (estimate from order deadlines and completion)
        total_hours = 0
        for order in completed_orders.filter(submitted_at__isnull=False):
            if order.created_at and order.submitted_at:
                duration = order.submitted_at - order.created_at
                total_hours += duration.total_seconds() / 3600
        
        self.total_hours_worked = total_hours
        if total_hours > 0:
            self.effective_hourly_rate = self.total_earnings / total_hours
            self.average_completion_time_hours = total_hours / self.total_orders_completed
        
        # Revision metrics
        from orders.models.enhanced_revisions import RevisionRequest
        revisions = RevisionRequest.objects.filter(
            order__writer=self.writer,
            order__website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end
        )
        self.total_revisions = revisions.count()
        if self.total_orders_completed > 0:
            orders_with_revisions = revisions.values('order').distinct().count()
            self.revision_rate = (orders_with_revisions / self.total_orders_completed) * 100
            self.average_revisions_per_order = self.total_revisions / self.total_orders_completed
        
        # Approval metrics
        approved = completed_orders.filter(status='approved').count()
        rejected = completed_orders.filter(status='rejected').count()
        if self.total_orders_completed > 0:
            self.approval_rate = (approved / self.total_orders_completed) * 100
            self.rejection_rate = (rejected / self.total_orders_completed) * 100
        
        # Quality metrics
        from writer_management.models.feedback import Feedback
        feedbacks = Feedback.objects.filter(
            to_user=self.writer,
            website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end
        )
        
        if feedbacks.exists():
            self.average_rating = feedbacks.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
            
            # Calculate quality score (weighted average of ratings)
            quality_avg = feedbacks.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0
            communication_avg = feedbacks.aggregate(Avg('communication_rating'))['communication_rating__avg'] or 0
            timeliness_avg = feedbacks.aggregate(Avg('timeliness_rating'))['timeliness_rating__avg'] or 0
            
            # Quality score: 40% quality, 30% communication, 30% timeliness
            self.quality_score = (
                (quality_avg * 0.4) +
                (communication_avg * 0.3) +
                (timeliness_avg * 0.3)
            ) if quality_avg else 0
        
        self.save()


class WriterAnalyticsSnapshot(models.Model):
    """
    Daily/weekly snapshots of writer analytics for trend analysis.
    """
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='writer_analytics_snapshots',
        limit_choices_to={'role': 'writer'}
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='writer_analytics_snapshots'
    )
    
    snapshot_date = models.DateField()
    snapshot_type = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='daily'
    )
    
    # Metrics snapshot
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    effective_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    revision_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    approval_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('writer', 'website', 'snapshot_date', 'snapshot_type')
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['writer', 'website', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"Snapshot for {self.writer.email} - {self.snapshot_date}"

