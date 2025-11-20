"""
Celery tasks for sending progress report reminders to writers.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from orders.models import Order, WriterProgress
from notifications_system.services.core import NotificationService


@shared_task
def send_progress_reminders():
    """
    Send reminders to writers to report progress at 30%, 50%, and 80% of deadline.
    Checks orders that are in progress and haven't reached their deadline.
    """
    now = timezone.now()
    
    # Get orders that are in progress and have a writer assigned
    orders = Order.objects.filter(
        status__in=['in_progress', 'assigned'],
        assigned_writer__isnull=False,
        writer_deadline__isnull=False,
        writer_deadline__gt=now  # Not past deadline
    ).select_related('assigned_writer', 'client', 'website')
    
    for order in orders:
        if not order.writer_deadline:
            continue
        
        # Calculate time elapsed and remaining
        created_at = order.created_at or order.updated_at
        deadline = order.writer_deadline
        total_duration = deadline - created_at
        elapsed = now - created_at
        
        if total_duration.total_seconds() <= 0:
            continue
        
        # Calculate progress milestones
        progress_30_time = created_at + (total_duration * Decimal('0.3'))
        progress_50_time = created_at + (total_duration * Decimal('0.5'))
        progress_80_time = created_at + (total_duration * Decimal('0.8'))
        
        # Get latest progress report
        latest_progress = WriterProgress.objects.filter(
            order=order,
            is_withdrawn=False
        ).order_by('-timestamp').first()
        
        latest_percentage = latest_progress.progress_percentage if latest_progress else 0
        
        # Check if we're at 30% milestone and no progress report exists or is below 30%
        if (progress_30_time <= now < progress_30_time + timedelta(hours=2) and 
            latest_percentage < 30):
            _send_reminder(order, 30)
        
        # Check if we're at 50% milestone and progress is below 50%
        elif (progress_50_time <= now < progress_50_time + timedelta(hours=2) and 
              latest_percentage < 50):
            _send_reminder(order, 50)
        
        # Check if we're at 80% milestone and progress is below 80%
        elif (progress_80_time <= now < progress_80_time + timedelta(hours=2) and 
              latest_percentage < 80):
            _send_reminder(order, 80)


def _send_reminder(order, milestone_percentage):
    """Send a progress reminder notification to the writer."""
    writer = order.assigned_writer
    if not writer:
        return
    
    # Check if we've already sent a reminder for this milestone recently (within 24 hours)
    from notifications_system.models import Notification
    recent_reminder = Notification.objects.filter(
        user=writer,
        event='progress_reminder',
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).exists()
    
    if recent_reminder:
        return
    
    # Send notification
    NotificationService.send_notification(
        user=writer,
        event='progress_reminder',
        payload={
            'order_id': order.id,
            'order_topic': order.topic,
            'milestone_percentage': milestone_percentage,
            'deadline': order.writer_deadline.isoformat() if order.writer_deadline else None,
        },
        website=order.website,
        category='reminder',
        priority=5,
        channels=['in_app'],
    )

