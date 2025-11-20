"""
Notification delivery analytics and tracking.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from django.db import models
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class DeliveryMetrics(models.Model):
    """Track notification delivery metrics."""
    
    event_key = models.CharField(max_length=100, db_index=True)
    channel = models.CharField(max_length=20, db_index=True)
    website_id = models.IntegerField(null=True, blank=True, db_index=True)
    user_id = models.IntegerField(null=True, blank=True, db_index=True)
    
    # Delivery metrics
    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    bounced_count = models.PositiveIntegerField(default=0)
    opened_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_delivery_time = models.FloatField(default=0.0)
    min_delivery_time = models.FloatField(default=0.0)
    max_delivery_time = models.FloatField(default=0.0)
    
    # Time tracking
    first_sent = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event_key', 'channel', 'website_id', 'user_id']
        indexes = [
            models.Index(fields=['event_key', 'channel']),
            models.Index(fields=['website_id', 'channel']),
            models.Index(fields=['user_id', 'channel']),
            models.Index(fields=['last_sent']),
        ]
    
    def __str__(self):
        return f"{self.event_key} - {self.channel} - {self.user_id}"
    
    @property
    def delivery_rate(self) -> float:
        """Calculate delivery rate percentage."""
        if self.sent_count == 0:
            return 0.0
        return (self.delivered_count / self.sent_count) * 100
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.sent_count == 0:
            return 0.0
        return (self.failed_count / self.sent_count) * 100
    
    @property
    def bounce_rate(self) -> float:
        """Calculate bounce rate percentage."""
        if self.sent_count == 0:
            return 0.0
        return (self.bounced_count / self.sent_count) * 100
    
    @property
    def open_rate(self) -> float:
        """Calculate open rate percentage."""
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100
    
    @property
    def click_through_rate(self) -> float:
        """Calculate click-through rate percentage."""
        if self.delivered_count == 0:
            return 0.0
        return (self.clicked_count / self.delivered_count) * 100


class DeliveryPerformance(models.Model):
    """Track delivery performance over time."""
    
    event_key = models.CharField(max_length=100, db_index=True)
    channel = models.CharField(max_length=20, db_index=True)
    website_id = models.IntegerField(null=True, blank=True)
    
    # Time period
    date = models.DateField(db_index=True)
    hour = models.PositiveSmallIntegerField(default=0)  # 0-23
    
    # Delivery metrics
    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    bounced_count = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    opened_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_delivery_time = models.FloatField(default=0.0)
    min_delivery_time = models.FloatField(default=0.0)
    max_delivery_time = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [
            'event_key', 'channel', 'website_id', 'date', 'hour'
        ]
        indexes = [
            models.Index(fields=['event_key', 'date']),
            models.Index(fields=['channel', 'date']),
            models.Index(fields=['website_id', 'date']),
        ]
    
    def __str__(self):
        return f"{self.event_key} - {self.channel} - {self.date} {self.hour}:00"


class DeliveryAnalytics:
    """Analytics engine for delivery metrics."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def record_delivery(
        self,
        event_key: str,
        channel: str,
        success: bool,
        delivery_time: float,
        website_id: Optional[int] = None,
        user_id: Optional[int] = None
    ):
        """Record delivery event."""
        try:
            # Update delivery metrics
            metrics, created = DeliveryMetrics.objects.get_or_create(
                event_key=event_key,
                channel=channel,
                website_id=website_id,
                user_id=user_id,
                defaults={
                    'sent_count': 0,
                    'delivered_count': 0,
                    'failed_count': 0,
                    'bounced_count': 0,
                    'opened_count': 0,
                    'clicked_count': 0,
                    'avg_delivery_time': 0.0,
                    'min_delivery_time': delivery_time,
                    'max_delivery_time': delivery_time
                }
            )
            
            # Update metrics
            metrics.sent_count += 1
            
            if success:
                metrics.delivered_count += 1
            else:
                metrics.failed_count += 1
            
            # Update delivery time
            if metrics.min_delivery_time == 0 or delivery_time < metrics.min_delivery_time:
                metrics.min_delivery_time = delivery_time
            if delivery_time > metrics.max_delivery_time:
                metrics.max_delivery_time = delivery_time
            
            # Update average delivery time
            total_time = metrics.avg_delivery_time * (metrics.sent_count - 1) + delivery_time
            metrics.avg_delivery_time = total_time / metrics.sent_count
            
            metrics.save(update_fields=[
                'sent_count', 'delivered_count', 'failed_count',
                'avg_delivery_time', 'min_delivery_time', 'max_delivery_time', 'last_sent'
            ])
            
            # Update hourly performance
            self._update_hourly_performance(
                event_key, channel, website_id, success, delivery_time
            )
            
        except Exception as e:
            logger.exception(f"Error recording delivery: {e}")
    
    def record_engagement(
        self,
        event_key: str,
        channel: str,
        engagement_type: str,  # 'opened', 'clicked', 'bounced'
        website_id: Optional[int] = None,
        user_id: Optional[int] = None
    ):
        """Record engagement event."""
        try:
            metrics, created = DeliveryMetrics.objects.get_or_create(
                event_key=event_key,
                channel=channel,
                website_id=website_id,
                user_id=user_id,
                defaults={
                    'sent_count': 0,
                    'delivered_count': 0,
                    'failed_count': 0,
                    'bounced_count': 0,
                    'opened_count': 0,
                    'clicked_count': 0,
                    'avg_delivery_time': 0.0,
                    'min_delivery_time': 0.0,
                    'max_delivery_time': 0.0
                }
            )
            
            # Update engagement metrics
            if engagement_type == 'opened':
                metrics.opened_count += 1
            elif engagement_type == 'clicked':
                metrics.clicked_count += 1
            elif engagement_type == 'bounced':
                metrics.bounced_count += 1
            
            metrics.save(update_fields=[
                'opened_count', 'clicked_count', 'bounced_count', 'last_sent'
            ])
            
        except Exception as e:
            logger.exception(f"Error recording engagement: {e}")
    
    def _update_hourly_performance(
        self,
        event_key: str,
        channel: str,
        website_id: Optional[int],
        success: bool,
        delivery_time: float
    ):
        """Update hourly performance metrics."""
        now = timezone.now()
        date = now.date()
        hour = now.hour
        
        performance, created = DeliveryPerformance.objects.get_or_create(
            event_key=event_key,
            channel=channel,
            website_id=website_id,
            date=date,
            hour=hour,
            defaults={
                'sent_count': 0,
                'delivered_count': 0,
                'failed_count': 0,
                'bounced_count': 0,
                'opened_count': 0,
                'clicked_count': 0,
                'avg_delivery_time': 0.0,
                'min_delivery_time': delivery_time,
                'max_delivery_time': delivery_time
            }
        )
        
        # Update metrics
        performance.sent_count += 1
        
        if success:
            performance.delivered_count += 1
        else:
            performance.failed_count += 1
        
        # Update delivery time
        if performance.min_delivery_time == 0 or delivery_time < performance.min_delivery_time:
            performance.min_delivery_time = delivery_time
        if delivery_time > performance.max_delivery_time:
            performance.max_delivery_time = delivery_time
        
        # Update average delivery time
        total_time = performance.avg_delivery_time * (performance.sent_count - 1) + delivery_time
        performance.avg_delivery_time = total_time / performance.sent_count
        
        performance.save(update_fields=[
            'sent_count', 'delivered_count', 'failed_count',
            'avg_delivery_time', 'min_delivery_time', 'max_delivery_time'
        ])
    
    def get_delivery_stats(
        self,
        event_key: Optional[str] = None,
        channel: Optional[str] = None,
        days: int = 30,
        website_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive delivery statistics."""
        cache_key = f"delivery_stats:{event_key}:{channel}:{days}:{website_id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        # Calculate stats
        since_date = timezone.now().date() - timedelta(days=days)
        
        # Delivery metrics
        metrics_query = DeliveryMetrics.objects.filter(
            last_sent__date__gte=since_date
        )
        
        if event_key:
            metrics_query = metrics_query.filter(event_key=event_key)
        if channel:
            metrics_query = metrics_query.filter(channel=channel)
        if website_id:
            metrics_query = metrics_query.filter(website_id=website_id)
        
        delivery_stats = metrics_query.aggregate(
            total_sent=models.Sum('sent_count'),
            total_delivered=models.Sum('delivered_count'),
            total_failed=models.Sum('failed_count'),
            total_bounced=models.Sum('bounced_count'),
            total_opened=models.Sum('opened_count'),
            total_clicked=models.Sum('clicked_count'),
            avg_delivery_time=models.Avg('avg_delivery_time'),
            min_delivery_time=models.Min('min_delivery_time'),
            max_delivery_time=models.Max('max_delivery_time')
        )
        
        # Calculate rates
        total_sent = delivery_stats['total_sent'] or 0
        total_delivered = delivery_stats['total_delivered'] or 0
        total_failed = delivery_stats['total_failed'] or 0
        total_bounced = delivery_stats['total_bounced'] or 0
        total_opened = delivery_stats['total_opened'] or 0
        total_clicked = delivery_stats['total_clicked'] or 0
        
        stats = {
            'event_key': event_key,
            'channel': channel,
            'period_days': days,
            'website_id': website_id,
            'total_sent': total_sent,
            'total_delivered': total_delivered,
            'total_failed': total_failed,
            'total_bounced': total_bounced,
            'total_opened': total_opened,
            'total_clicked': total_clicked,
            'delivery_rate': (total_delivered / total_sent * 100) if total_sent > 0 else 0,
            'failure_rate': (total_failed / total_sent * 100) if total_sent > 0 else 0,
            'bounce_rate': (total_bounced / total_sent * 100) if total_sent > 0 else 0,
            'open_rate': (total_opened / total_delivered * 100) if total_delivered > 0 else 0,
            'click_through_rate': (total_clicked / total_delivered * 100) if total_delivered > 0 else 0,
            'avg_delivery_time': delivery_stats['avg_delivery_time'] or 0,
            'min_delivery_time': delivery_stats['min_delivery_time'] or 0,
            'max_delivery_time': delivery_stats['max_delivery_time'] or 0
        }
        
        # Cache the results
        cache.set(cache_key, stats, self.cache_timeout)
        
        return stats
    
    def get_channel_performance(
        self,
        days: int = 30,
        website_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get performance by channel."""
        since_date = timezone.now().date() - timedelta(days=days)
        
        query = DeliveryMetrics.objects.filter(
            last_sent__date__gte=since_date
        )
        
        if website_id:
            query = query.filter(website_id=website_id)
        
        # Group by channel
        channel_stats = query.values('channel').annotate(
            total_sent=models.Sum('sent_count'),
            total_delivered=models.Sum('delivered_count'),
            total_failed=models.Sum('failed_count'),
            total_bounced=models.Sum('bounced_count'),
            total_opened=models.Sum('opened_count'),
            total_clicked=models.Sum('clicked_count'),
            avg_delivery_time=models.Avg('avg_delivery_time')
        ).order_by('-total_sent')
        
        return [
            {
                'channel': stat['channel'],
                'total_sent': stat['total_sent'] or 0,
                'total_delivered': stat['total_delivered'] or 0,
                'total_failed': stat['total_failed'] or 0,
                'total_bounced': stat['total_bounced'] or 0,
                'total_opened': stat['total_opened'] or 0,
                'total_clicked': stat['total_clicked'] or 0,
                'delivery_rate': (stat['total_delivered'] / stat['total_sent'] * 100) if stat['total_sent'] > 0 else 0,
                'open_rate': (stat['total_opened'] / stat['total_delivered'] * 100) if stat['total_delivered'] > 0 else 0,
                'click_through_rate': (stat['total_clicked'] / stat['total_delivered'] * 100) if stat['total_delivered'] > 0 else 0,
                'avg_delivery_time': stat['avg_delivery_time'] or 0
            }
            for stat in channel_stats
        ]
    
    def get_delivery_trends(
        self,
        event_key: str,
        channel: Optional[str] = None,
        days: int = 30,
        website_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get delivery trends over time."""
        since_date = timezone.now().date() - timedelta(days=days)
        
        query = DeliveryPerformance.objects.filter(
            event_key=event_key,
            date__gte=since_date
        )
        
        if channel:
            query = query.filter(channel=channel)
        if website_id:
            query = query.filter(website_id=website_id)
        
        trends = query.order_by('date', 'hour')
        
        return [
            {
                'date': trend.date.isoformat(),
                'hour': trend.hour,
                'channel': trend.channel,
                'sent_count': trend.sent_count,
                'delivered_count': trend.delivered_count,
                'failed_count': trend.failed_count,
                'bounced_count': trend.bounced_count,
                'opened_count': trend.opened_count,
                'clicked_count': trend.clicked_count,
                'delivery_rate': (trend.delivered_count / trend.sent_count * 100) if trend.sent_count > 0 else 0,
                'avg_delivery_time': trend.avg_delivery_time
            }
            for trend in trends
        ]


# Global delivery analytics instance
_delivery_analytics = DeliveryAnalytics()

def get_delivery_analytics() -> DeliveryAnalytics:
    """Get the global delivery analytics instance."""
    return _delivery_analytics


def record_delivery(
    event_key: str,
    channel: str,
    success: bool,
    delivery_time: float,
    website_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Record delivery event."""
    analytics = get_delivery_analytics()
    analytics.record_delivery(
        event_key, channel, success, delivery_time, website_id, user_id
    )


def record_engagement(
    event_key: str,
    channel: str,
    engagement_type: str,
    website_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Record engagement event."""
    analytics = get_delivery_analytics()
    analytics.record_engagement(
        event_key, channel, engagement_type, website_id, user_id
    )
