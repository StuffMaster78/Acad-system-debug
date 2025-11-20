"""
Performance monitoring for the notification system.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional
from django.core.cache import cache
from django.db import connection
from notifications_system.utils.logging import notification_logger


class PerformanceMonitor:
    """Monitor notification system performance metrics."""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 measurements
        self.counters = defaultdict(int)
        self.timers = {}
    
    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a performance metric."""
        metric_key = self._build_metric_key(metric_name, tags)
        self.metrics[metric_key].append({
            'value': value,
            'timestamp': time.time()
        })
        
        # Log to structured logger
        notification_logger.log_performance_metric(
            metric_name=metric_name,
            value=value,
            unit='ms',
            **tags or {}
        )
    
    def increment_counter(self, counter_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        counter_key = self._build_metric_key(counter_name, tags)
        self.counters[counter_key] += value
    
    def start_timer(self, timer_name: str, tags: Optional[Dict[str, str]] = None):
        """Start a performance timer."""
        timer_key = self._build_metric_key(timer_name, tags)
        self.timers[timer_key] = time.time()
    
    def end_timer(self, timer_name: str, tags: Optional[Dict[str, str]] = None):
        """End a performance timer and record the duration."""
        timer_key = self._build_metric_key(timer_name, tags)
        if timer_key in self.timers:
            duration = time.time() - self.timers[timer_key]
            self.record_metric(f"{timer_name}_duration", duration, tags)
            del self.timers[timer_key]
            return duration
        return None
    
    def _build_metric_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Build metric key with tags."""
        if not tags:
            return name
        
        tag_parts = [f"{k}={v}" for k, v in sorted(tags.items())]
        return f"{name}[{','.join(tag_parts)}]"
    
    def get_metric_stats(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get statistics for a metric."""
        metric_key = self._build_metric_key(metric_name, tags)
        values = self.metrics.get(metric_key, deque())
        
        if not values:
            return {'count': 0}
        
        values_list = [v['value'] for v in values]
        
        return {
            'count': len(values_list),
            'min': min(values_list),
            'max': max(values_list),
            'avg': sum(values_list) / len(values_list),
            'p50': self._percentile(values_list, 50),
            'p95': self._percentile(values_list, 95),
            'p99': self._percentile(values_list, 99),
        }
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics and counters."""
        metrics = {}
        
        # Process metrics
        for metric_key, values in self.metrics.items():
            if values:
                values_list = [v['value'] for v in values]
                metrics[metric_key] = {
                    'type': 'metric',
                    'count': len(values_list),
                    'min': min(values_list),
                    'max': max(values_list),
                    'avg': sum(values_list) / len(values_list),
                }
        
        # Process counters
        for counter_key, value in self.counters.items():
            metrics[counter_key] = {
                'type': 'counter',
                'value': value,
            }
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.counters.clear()
        self.timers.clear()


class NotificationPerformanceMonitor:
    """Specialized performance monitor for notifications."""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
    
    def record_notification_sent(
        self,
        event_key: str,
        channel: str,
        duration: float,
        user_id: Optional[int] = None
    ):
        """Record notification sent performance."""
        tags = {
            'event_key': event_key,
            'channel': channel,
        }
        if user_id:
            tags['user_id'] = str(user_id)
        
        self.monitor.record_metric('notification_sent_duration', duration, tags)
        self.monitor.increment_counter('notifications_sent', tags=tags)
    
    def record_template_rendering(
        self,
        event_key: str,
        template_type: str,
        duration: float
    ):
        """Record template rendering performance."""
        tags = {
            'event_key': event_key,
            'template_type': template_type,
        }
        
        self.monitor.record_metric('template_rendering_duration', duration, tags)
        self.monitor.increment_counter('templates_rendered', tags=tags)
    
    def record_sse_connection(
        self,
        user_id: int,
        duration: float,
        action: str
    ):
        """Record SSE connection performance."""
        tags = {
            'user_id': str(user_id),
            'action': action,
        }
        
        self.monitor.record_metric('sse_connection_duration', duration, tags)
        self.monitor.increment_counter('sse_connections', tags=tags)
    
    def record_database_query(
        self,
        query_type: str,
        duration: float,
        table: Optional[str] = None
    ):
        """Record database query performance."""
        tags = {
            'query_type': query_type,
        }
        if table:
            tags['table'] = table
        
        self.monitor.record_metric('db_query_duration', duration, tags)
        self.monitor.increment_counter('db_queries', tags=tags)
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification-specific statistics."""
        return {
            'notifications_sent': self.monitor.get_metric_stats('notification_sent_duration'),
            'template_rendering': self.monitor.get_metric_stats('template_rendering_duration'),
            'sse_connections': self.monitor.get_metric_stats('sse_connection_duration'),
            'db_queries': self.monitor.get_metric_stats('db_query_duration'),
        }


class DatabaseQueryMonitor:
    """Monitor database query performance."""
    
    def __init__(self):
        self.query_count = 0
        self.total_time = 0.0
        self.slow_queries = []
    
    def start_monitoring(self):
        """Start monitoring database queries."""
        self.query_count = 0
        self.total_time = 0.0
        self.slow_queries = []
        connection.queries_log.clear()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return statistics."""
        queries = connection.queries
        self.query_count = len(queries)
        
        for query in queries:
            query_time = float(query['time'])
            self.total_time += query_time
            
            # Track slow queries (>100ms)
            if query_time > 0.1:
                self.slow_queries.append({
                    'sql': query['sql'][:200] + '...' if len(query['sql']) > 200 else query['sql'],
                    'time': query_time
                })
        
        return {
            'query_count': self.query_count,
            'total_time': self.total_time,
            'avg_query_time': self.total_time / self.query_count if self.query_count > 0 else 0,
            'slow_queries': self.slow_queries[:10],  # Top 10 slow queries
        }


# Global performance monitor
_performance_monitor = NotificationPerformanceMonitor()

def get_performance_monitor() -> NotificationPerformanceMonitor:
    """Get the global performance monitor."""
    return _performance_monitor


def record_notification_performance(
    event_key: str,
    channel: str,
    duration: float,
    user_id: Optional[int] = None
):
    """Convenience function to record notification performance."""
    monitor = get_performance_monitor()
    monitor.record_notification_sent(event_key, channel, duration, user_id)
