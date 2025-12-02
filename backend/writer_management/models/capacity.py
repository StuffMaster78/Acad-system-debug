"""
Writer Capacity & Availability Controls
Allows writers to set max active orders, blackout dates, and preferred subjects.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from websites.models import Website


class WriterCapacity(models.Model):
    """
    Writer capacity and availability settings.
    """
    writer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='capacity_settings',
        limit_choices_to={'role': 'writer'}
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_capacities'
    )
    
    # Capacity limits
    max_active_orders = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of active orders at once"
    )
    current_active_orders = models.PositiveIntegerField(
        default=0,
        help_text="Current number of active orders (auto-updated)"
    )
    
    # Availability
    is_available = models.BooleanField(
        default=True,
        help_text="Whether writer is currently accepting new orders"
    )
    availability_message = models.TextField(
        blank=True,
        help_text="Optional message about availability (e.g., 'On vacation until...')"
    )
    
    # Preferred subjects/areas
    preferred_subjects = models.ManyToManyField(
        'order_configs.Subject',
        blank=True,
        related_name='preferred_writers',
        help_text="Subjects this writer prefers to work on"
    )
    preferred_types_of_work = models.ManyToManyField(
        'order_configs.TypeOfWork',
        blank=True,
        related_name='preferred_writers',
        help_text="Types of work this writer prefers"
    )
    
    # Blackout dates
    blackout_dates = models.JSONField(
        default=list,
        blank=True,
        help_text="List of blackout dates: [{'start': '2024-01-01', 'end': '2024-01-07', 'reason': 'Vacation'}]"
    )
    
    # Workload preferences
    preferred_deadline_buffer_days = models.PositiveIntegerField(
        default=3,
        help_text="Preferred minimum days before deadline when accepting orders"
    )
    max_orders_per_day = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum orders to accept per day (null = unlimited)"
    )
    
    # Auto-assignment preferences
    auto_accept_orders = models.BooleanField(
        default=False,
        help_text="Automatically accept orders matching preferences"
    )
    auto_accept_preferred_only = models.BooleanField(
        default=False,
        help_text="Only auto-accept from preferred clients"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('writer', 'website')
        indexes = [
            models.Index(fields=['writer', 'website', 'is_available']),
            models.Index(fields=['is_available', 'current_active_orders']),
        ]
        verbose_name = "Writer Capacity"
        verbose_name_plural = "Writer Capacities"
    
    def __str__(self):
        return f"Capacity for {self.writer.email} - {self.current_active_orders}/{self.max_active_orders}"
    
    def can_accept_order(self):
        """Check if writer can accept a new order."""
        if not self.is_available:
            return False, "Writer is not available"
        
        if self.current_active_orders >= self.max_active_orders:
            return False, f"Writer has reached max capacity ({self.max_active_orders} orders)"
        
        return True, None
    
    def is_blacked_out(self, date):
        """Check if a date is in blackout period."""
        if not self.blackout_dates:
            return False
        
        check_date = date.date() if hasattr(date, 'date') else date
        
        for period in self.blackout_dates:
            start = timezone.datetime.fromisoformat(period['start']).date()
            end = timezone.datetime.fromisoformat(period['end']).date()
            if start <= check_date <= end:
                return True
        
        return False
    
    def add_blackout_period(self, start_date, end_date, reason=''):
        """Add a blackout period."""
        if not self.blackout_dates:
            self.blackout_dates = []
        
        self.blackout_dates.append({
            'start': start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
            'end': end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date),
            'reason': reason
        })
        self.save(update_fields=['blackout_dates'])
    
    def update_active_orders_count(self):
        """Update current_active_orders count from database."""
        from orders.models import Order
        count = Order.objects.filter(
            writer=self.writer,
            website=self.website,
            status__in=['in_progress', 'revision_in_progress', 'on_hold']
        ).count()
        
        self.current_active_orders = count
        self.save(update_fields=['current_active_orders'])


class EditorWorkload(models.Model):
    """
    Editor workload caps and preferences.
    """
    editor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workload_settings',
        limit_choices_to={'role': 'editor'}
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='editor_workloads'
    )
    
    # Workload limits
    max_active_tasks = models.PositiveIntegerField(
        default=10,
        help_text="Maximum number of active editing tasks"
    )
    current_active_tasks = models.PositiveIntegerField(
        default=0,
        help_text="Current number of active tasks (auto-updated)"
    )
    
    # Availability
    is_available = models.BooleanField(
        default=True,
        help_text="Whether editor is currently accepting new tasks"
    )
    
    # Preferences
    preferred_subjects = models.ManyToManyField(
        'order_configs.Subject',
        blank=True,
        related_name='preferred_editors'
    )
    preferred_types_of_work = models.ManyToManyField(
        'order_configs.TypeOfWork',
        blank=True,
        related_name='preferred_editors'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('editor', 'website')
        verbose_name = "Editor Workload"
        verbose_name_plural = "Editor Workloads"
    
    def __str__(self):
        return f"Workload for {self.editor.email} - {self.current_active_tasks}/{self.max_active_tasks}"

