"""
Client Analytics Models
Spend over time, on-time delivery %, revision rates, writer performance.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
# Use string references to avoid circular imports


class ClientAnalytics(models.Model):
    """
    Aggregated analytics for clients.
    """
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_analytics',
        limit_choices_to={'role': 'client'}
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='client_analytics'
    )
    
    # Time period
    period_start = models.DateField(
        help_text="Start of analytics period"
    )
    period_end = models.DateField(
        help_text="End of analytics period"
    )
    
    # Spend metrics
    total_spend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total amount spent in period"
    )
    average_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Average order value"
    )
    total_orders = models.PositiveIntegerField(
        default=0,
        help_text="Total orders in period"
    )
    
    # Delivery metrics
    on_time_delivery_count = models.PositiveIntegerField(
        default=0,
        help_text="Orders delivered on time"
    )
    late_delivery_count = models.PositiveIntegerField(
        default=0,
        help_text="Orders delivered late"
    )
    on_time_delivery_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders delivered on time"
    )
    
    # Revision metrics
    total_revisions = models.PositiveIntegerField(
        default=0,
        help_text="Total revision requests"
    )
    revision_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders with revisions"
    )
    average_revisions_per_order = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Average number of revisions per order"
    )
    
    # Writer performance (aggregated)
    top_writers = models.JSONField(
        default=list,
        blank=True,
        help_text="Top performing writers: [{'writer_id': 1, 'orders': 5, 'avg_rating': 4.5}]"
    )
    average_writer_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average rating of writers used"
    )
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('client', 'website', 'period_start', 'period_end')
        indexes = [
            models.Index(fields=['client', 'website', 'period_start']),
        ]
        verbose_name = "Client Analytics"
        verbose_name_plural = "Client Analytics"
    
    def __str__(self):
        return f"Analytics for {self.client.email} - {self.period_start} to {self.period_end}"
    
    def recalculate(self):
        """Recalculate all metrics from orders."""
        orders = Order.objects.filter(
            client=self.client,
            website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end
        )
        
        # Spend metrics
        self.total_orders = orders.count()
        if self.total_orders > 0:
            self.total_spend = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
            self.average_order_value = self.total_spend / self.total_orders
        
        # Delivery metrics
        from django.db.models import F
        completed_orders = orders.filter(status='completed', submitted_at__isnull=False)
        if completed_orders.exists():
            on_time = completed_orders.filter(submitted_at__lte=F('deadline')).count()
            self.on_time_delivery_count = on_time
            self.late_delivery_count = completed_orders.count() - on_time
            self.on_time_delivery_rate = (on_time / completed_orders.count()) * 100
        
        # Revision metrics
        from orders.models.enhanced_revisions import RevisionRequest
        revisions = RevisionRequest.objects.filter(
            order__client=self.client,
            order__website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end
        )
        self.total_revisions = revisions.count()
        if self.total_orders > 0:
            orders_with_revisions = revisions.values('order').distinct().count()
            self.revision_rate = (orders_with_revisions / self.total_orders) * 100
            self.average_revisions_per_order = self.total_revisions / self.total_orders
        
        # Writer performance
        from writer_management.models.feedback import Feedback
        writer_stats = {}
        for order in orders.filter(writer__isnull=False):
            writer_id = order.writer_id
            if writer_id not in writer_stats:
                writer_stats[writer_id] = {'orders': 0, 'ratings': []}
            writer_stats[writer_id]['orders'] += 1
            
            # Get feedback ratings
            feedbacks = Feedback.objects.filter(
                order=order,
                feedback_type='client_to_writer'
            )
            for feedback in feedbacks:
                writer_stats[writer_id]['ratings'].append(feedback.overall_rating)
        
        # Calculate top writers
        top_writers = []
        for writer_id, stats in writer_stats.items():
            avg_rating = sum(stats['ratings']) / len(stats['ratings']) if stats['ratings'] else 0
            top_writers.append({
                'writer_id': writer_id,
                'orders': stats['orders'],
                'avg_rating': float(avg_rating)
            })
        
        self.top_writers = sorted(top_writers, key=lambda x: x['orders'], reverse=True)[:10]
        
        # Average writer rating
        all_ratings = []
        for stats in writer_stats.values():
            all_ratings.extend(stats['ratings'])
        if all_ratings:
            self.average_writer_rating = sum(all_ratings) / len(all_ratings)
        
        self.save()


class ClientAnalyticsSnapshot(models.Model):
    """
    Daily/weekly snapshots of client analytics for trend analysis.
    """
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_analytics_snapshots',
        limit_choices_to={'role': 'client'}
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='client_analytics_snapshots'
    )
    
    snapshot_date = models.DateField(
        help_text="Date of snapshot"
    )
    snapshot_type = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='daily'
    )
    
    # Metrics snapshot
    total_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_orders = models.PositiveIntegerField(default=0)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    revision_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('client', 'website', 'snapshot_date', 'snapshot_type')
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['client', 'website', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"Snapshot for {self.client.email} - {self.snapshot_date}"

