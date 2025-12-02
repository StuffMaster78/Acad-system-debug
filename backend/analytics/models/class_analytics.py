"""
Class / Bulk Order Analytics Models
Attendance/completion, performance per group, exportable reports.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
# Use string references to avoid circular imports


class ClassAnalytics(models.Model):
    """
    Analytics for class/bulk orders.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='class_analytics'
    )
    
    # Class/bulk order identifier
    class_name = models.CharField(
        max_length=255,
        help_text="Name/identifier for the class/bulk order"
    )
    class_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional class ID"
    )
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Attendance metrics
    total_students = models.PositiveIntegerField(
        default=0,
        help_text="Total students in class"
    )
    active_students = models.PositiveIntegerField(
        default=0,
        help_text="Students who have placed orders"
    )
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of students who placed orders"
    )
    
    # Completion metrics
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders completed"
    )
    
    # Performance metrics
    average_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average grade/score (if applicable)"
    )
    on_time_submission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of orders submitted on time"
    )
    
    # Group performance
    group_performance = models.JSONField(
        default=list,
        blank=True,
        help_text="Performance by group: [{'group_name': 'Group A', 'completion_rate': 85.5, 'avg_grade': 4.2}]"
    )
    
    # Calculated at
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('website', 'class_name', 'class_id', 'period_start', 'period_end')
        indexes = [
            models.Index(fields=['website', 'class_name', 'period_start']),
        ]
        verbose_name = "Class Analytics"
        verbose_name_plural = "Class Analytics"
    
    def __str__(self):
        return f"Analytics for {self.class_name} - {self.period_start} to {self.period_end}"
    
    def recalculate(self):
        """Recalculate metrics from orders."""
        # This would need to be customized based on how classes are identified
        # For now, assuming orders have a class_name or class_id field
        # You may need to add this to Order model or use metadata
        
        orders = Order.objects.filter(
            website=self.website,
            created_at__date__gte=self.period_start,
            created_at__date__lte=self.period_end
        )
        
        # Filter by class (this is a placeholder - adjust based on your class identification)
        # Assuming there's a way to identify class orders (metadata, tags, etc.)
        class_orders = orders  # Placeholder - filter appropriately
        
        self.total_orders = class_orders.count()
        self.completed_orders = class_orders.filter(status='completed').count()
        
        if self.total_orders > 0:
            self.completion_rate = (self.completed_orders / self.total_orders) * 100
        
        # On-time submission
        from django.db.models import F
        completed = class_orders.filter(status='completed', submitted_at__isnull=False)
        if completed.exists():
            on_time = completed.filter(submitted_at__lte=F('deadline')).count()
            self.on_time_submission_rate = (on_time / completed.count()) * 100
        
        # Group performance (placeholder - customize based on your grouping logic)
        self.group_performance = []
        
        self.save()


class ClassPerformanceReport(models.Model):
    """
    Exportable performance reports for classes.
    """
    class_analytics = models.ForeignKey(
        ClassAnalytics,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('summary', 'Summary'),
            ('detailed', 'Detailed'),
            ('student_list', 'Student List'),
            ('performance_by_group', 'Performance by Group'),
        ],
        default='summary'
    )
    
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    report_data = models.JSONField(
        default=dict,
        help_text="Report data in JSON format"
    )
    
    file = models.FileField(
        upload_to='class_reports/',
        null=True,
        blank=True,
        help_text="Exported report file (PDF, CSV, etc.)"
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"Report for {self.class_analytics.class_name} - {self.report_type}"

