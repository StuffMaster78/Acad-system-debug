"""
Template analytics and usage tracking system.
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


class TemplateUsage(models.Model):
    """Track template usage and performance metrics."""
    
    event_key = models.CharField(max_length=100, db_index=True)
    template_type = models.CharField(max_length=20, choices=[
        ('class_based', 'Class Based'),
        ('database', 'Database'),
        ('generic', 'Generic'),
        ('emergency', 'Emergency')
    ])
    template_version = models.CharField(max_length=20, default="v1.0")
    channel = models.CharField(max_length=20, db_index=True)
    website_id = models.IntegerField(null=True, blank=True, db_index=True)
    locale = models.CharField(max_length=10, default="en")
    
    # Usage metrics
    render_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    total_render_time = models.FloatField(default=0.0)
    avg_render_time = models.FloatField(default=0.0)
    
    # User engagement
    click_count = models.PositiveIntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0)
    
    # Time tracking
    first_used = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [
            'event_key', 'template_type', 'template_version', 
            'channel', 'website_id', 'locale'
        ]
        indexes = [
            models.Index(fields=['event_key', 'template_type']),
            models.Index(fields=['channel', 'website_id']),
            models.Index(fields=['last_used']),
        ]
    
    def __str__(self):
        return f"{self.event_key} ({self.template_type}) - {self.channel}"
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.render_count == 0:
            return 0.0
        return (self.success_count / self.render_count) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.render_count == 0:
            return 0.0
        return (self.error_count / self.render_count) * 100
    
    @property
    def click_through_rate(self) -> float:
        """Calculate click-through rate."""
        if self.render_count == 0:
            return 0.0
        return (self.click_count / self.render_count) * 100
    
    @property
    def open_rate(self) -> float:
        """Calculate open rate."""
        if self.render_count == 0:
            return 0.0
        return (self.open_count / self.render_count) * 100
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.render_count == 0:
            return 0.0
        return (self.conversion_count / self.render_count) * 100


class TemplatePerformance(models.Model):
    """Track template performance over time."""
    
    event_key = models.CharField(max_length=100, db_index=True)
    template_type = models.CharField(max_length=20)
    channel = models.CharField(max_length=20)
    website_id = models.IntegerField(null=True, blank=True)
    
    # Performance metrics
    date = models.DateField(db_index=True)
    hour = models.PositiveSmallIntegerField(default=0)  # 0-23
    
    render_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    avg_render_time = models.FloatField(default=0.0)
    min_render_time = models.FloatField(default=0.0)
    max_render_time = models.FloatField(default=0.0)
    
    # Engagement metrics
    click_count = models.PositiveIntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [
            'event_key', 'template_type', 'channel', 
            'website_id', 'date', 'hour'
        ]
        indexes = [
            models.Index(fields=['event_key', 'date']),
            models.Index(fields=['channel', 'date']),
            models.Index(fields=['website_id', 'date']),
        ]
    
    def __str__(self):
        return f"{self.event_key} - {self.date} {self.hour}:00"


class TemplateAnalytics:
    """Analytics engine for template usage and performance."""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
    
    def record_template_render(
        self,
        event_key: str,
        template_type: str,
        channel: str,
        success: bool,
        render_time: float,
        website_id: Optional[int] = None,
        locale: str = "en",
        template_version: str = "v1.0"
    ):
        """Record template render event."""
        try:
            # Update usage metrics
            usage, created = TemplateUsage.objects.get_or_create(
                event_key=event_key,
                template_type=template_type,
                template_version=template_version,
                channel=channel,
                website_id=website_id,
                locale=locale,
                defaults={
                    'render_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'total_render_time': 0.0,
                    'avg_render_time': 0.0
                }
            )
            
            # Update metrics
            usage.render_count += 1
            usage.total_render_time += render_time
            usage.avg_render_time = usage.total_render_time / usage.render_count
            
            if success:
                usage.success_count += 1
            else:
                usage.error_count += 1
            
            usage.save(update_fields=[
                'render_count', 'success_count', 'error_count',
                'total_render_time', 'avg_render_time', 'last_used'
            ])
            
            # Update hourly performance
            self._update_hourly_performance(
                event_key, template_type, channel, website_id,
                success, render_time
            )
            
        except Exception as e:
            logger.exception(f"Error recording template render: {e}")
    
    def record_template_engagement(
        self,
        event_key: str,
        template_type: str,
        channel: str,
        engagement_type: str,  # 'click', 'open', 'conversion'
        website_id: Optional[int] = None,
        locale: str = "en",
        template_version: str = "v1.0"
    ):
        """Record template engagement event."""
        try:
            usage, created = TemplateUsage.objects.get_or_create(
                event_key=event_key,
                template_type=template_type,
                template_version=template_version,
                channel=channel,
                website_id=website_id,
                locale=locale,
                defaults={
                    'render_count': 0,
                    'success_count': 0,
                    'error_count': 0,
                    'total_render_time': 0.0,
                    'avg_render_time': 0.0,
                    'click_count': 0,
                    'open_count': 0,
                    'conversion_count': 0
                }
            )
            
            # Update engagement metrics
            if engagement_type == 'click':
                usage.click_count += 1
            elif engagement_type == 'open':
                usage.open_count += 1
            elif engagement_type == 'conversion':
                usage.conversion_count += 1
            
            usage.save(update_fields=[
                'click_count', 'open_count', 'conversion_count', 'last_used'
            ])
            
        except Exception as e:
            logger.exception(f"Error recording template engagement: {e}")
    
    def _update_hourly_performance(
        self,
        event_key: str,
        template_type: str,
        channel: str,
        website_id: Optional[int],
        success: bool,
        render_time: float
    ):
        """Update hourly performance metrics."""
        now = timezone.now()
        date = now.date()
        hour = now.hour
        
        performance, created = TemplatePerformance.objects.get_or_create(
            event_key=event_key,
            template_type=template_type,
            channel=channel,
            website_id=website_id,
            date=date,
            hour=hour,
            defaults={
                'render_count': 0,
                'success_count': 0,
                'error_count': 0,
                'avg_render_time': 0.0,
                'min_render_time': render_time,
                'max_render_time': render_time
            }
        )
        
        # Update metrics
        performance.render_count += 1
        performance.avg_render_time = (
            (performance.avg_render_time * (performance.render_count - 1) + render_time) 
            / performance.render_count
        )
        
        if render_time < performance.min_render_time:
            performance.min_render_time = render_time
        if render_time > performance.max_render_time:
            performance.max_render_time = render_time
        
        if success:
            performance.success_count += 1
        else:
            performance.error_count += 1
        
        performance.save(update_fields=[
            'render_count', 'success_count', 'error_count',
            'avg_render_time', 'min_render_time', 'max_render_time'
        ])
    
    def get_template_stats(
        self,
        event_key: str,
        days: int = 30,
        website_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get comprehensive template statistics."""
        cache_key = f"template_stats:{event_key}:{days}:{website_id}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        # Calculate stats
        since_date = timezone.now().date() - timedelta(days=days)
        
        # Usage stats
        usage_query = TemplateUsage.objects.filter(
            event_key=event_key,
            last_used__date__gte=since_date
        )
        
        if website_id:
            usage_query = usage_query.filter(website_id=website_id)
        
        usage_stats = usage_query.aggregate(
            total_renders=models.Sum('render_count'),
            total_success=models.Sum('success_count'),
            total_errors=models.Sum('error_count'),
            total_clicks=models.Sum('click_count'),
            total_opens=models.Sum('open_count'),
            total_conversions=models.Sum('conversion_count'),
            avg_render_time=models.Avg('avg_render_time')
        )
        
        # Performance stats
        performance_query = TemplatePerformance.objects.filter(
            event_key=event_key,
            date__gte=since_date
        )
        
        if website_id:
            performance_query = performance_query.filter(website_id=website_id)
        
        performance_stats = performance_query.aggregate(
            total_renders=models.Sum('render_count'),
            total_success=models.Sum('success_count'),
            total_errors=models.Sum('error_count'),
            avg_render_time=models.Avg('avg_render_time'),
            min_render_time=models.Min('min_render_time'),
            max_render_time=models.Max('max_render_time')
        )
        
        # Calculate rates
        total_renders = usage_stats['total_renders'] or 0
        total_success = usage_stats['total_success'] or 0
        total_errors = usage_stats['total_errors'] or 0
        total_clicks = usage_stats['total_clicks'] or 0
        total_opens = usage_stats['total_opens'] or 0
        total_conversions = usage_stats['total_conversions'] or 0
        
        stats = {
            'event_key': event_key,
            'period_days': days,
            'website_id': website_id,
            'total_renders': total_renders,
            'total_success': total_success,
            'total_errors': total_errors,
            'total_clicks': total_clicks,
            'total_opens': total_opens,
            'total_conversions': total_conversions,
            'success_rate': (total_success / total_renders * 100) if total_renders > 0 else 0,
            'error_rate': (total_errors / total_renders * 100) if total_renders > 0 else 0,
            'click_through_rate': (total_clicks / total_renders * 100) if total_renders > 0 else 0,
            'open_rate': (total_opens / total_renders * 100) if total_renders > 0 else 0,
            'conversion_rate': (total_conversions / total_renders * 100) if total_renders > 0 else 0,
            'avg_render_time': usage_stats['avg_render_time'] or 0,
            'performance': performance_stats
        }
        
        # Cache the results
        cache.set(cache_key, stats, self.cache_timeout)
        
        return stats
    
    def get_top_templates(
        self,
        limit: int = 10,
        days: int = 30,
        website_id: Optional[int] = None,
        metric: str = 'render_count'
    ) -> List[Dict[str, Any]]:
        """Get top performing templates."""
        since_date = timezone.now().date() - timedelta(days=days)
        
        query = TemplateUsage.objects.filter(
            last_used__date__gte=since_date
        )
        
        if website_id:
            query = query.filter(website_id=website_id)
        
        # Order by specified metric
        order_field = f'-{metric}'
        top_templates = query.order_by(order_field)[:limit]
        
        return [
            {
                'event_key': template.event_key,
                'template_type': template.template_type,
                'channel': template.channel,
                'website_id': template.website_id,
                'render_count': template.render_count,
                'success_rate': template.success_rate,
                'click_through_rate': template.click_through_rate,
                'conversion_rate': template.conversion_rate,
                'avg_render_time': template.avg_render_time
            }
            for template in top_templates
        ]
    
    def get_template_trends(
        self,
        event_key: str,
        days: int = 30,
        website_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get template performance trends over time."""
        since_date = timezone.now().date() - timedelta(days=days)
        
        query = TemplatePerformance.objects.filter(
            event_key=event_key,
            date__gte=since_date
        )
        
        if website_id:
            query = query.filter(website_id=website_id)
        
        trends = query.order_by('date', 'hour')
        
        return [
            {
                'date': trend.date.isoformat(),
                'hour': trend.hour,
                'render_count': trend.render_count,
                'success_count': trend.success_count,
                'error_count': trend.error_count,
                'avg_render_time': trend.avg_render_time,
                'success_rate': (trend.success_count / trend.render_count * 100) if trend.render_count > 0 else 0
            }
            for trend in trends
        ]


# Global analytics instance
_analytics = TemplateAnalytics()

def get_template_analytics() -> TemplateAnalytics:
    """Get the global template analytics instance."""
    return _analytics


def record_template_render(
    event_key: str,
    template_type: str,
    channel: str,
    success: bool,
    render_time: float,
    website_id: Optional[int] = None,
    locale: str = "en",
    template_version: str = "v1.0"
):
    """Record template render event."""
    analytics = get_template_analytics()
    analytics.record_template_render(
        event_key, template_type, channel, success, render_time,
        website_id, locale, template_version
    )


def record_template_engagement(
    event_key: str,
    template_type: str,
    channel: str,
    engagement_type: str,
    website_id: Optional[int] = None,
    locale: str = "en",
    template_version: str = "v1.0"
):
    """Record template engagement event."""
    analytics = get_template_analytics()
    analytics.record_template_engagement(
        event_key, template_type, channel, engagement_type,
        website_id, locale, template_version
    )
