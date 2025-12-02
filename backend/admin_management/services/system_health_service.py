"""
System health monitoring service.
Tracks system metrics, performance, and alerts.
"""
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q, Avg, Max, Sum
from django.core.cache import cache
from django.db import connection
from orders.models import Order
from orders.order_enums import OrderStatus
from users.models import User
from writer_management.models import WriterProfile
from writer_wallet.models import WriterPayment
from fines.models import Fine
import logging

logger = logging.getLogger(__name__)

class SystemHealthService:
    """Service for monitoring system health and performance."""
    
    @staticmethod
    def get_system_health():
        """
        Get comprehensive system health metrics.
        
        Returns:
            dict: System health data including metrics, alerts, and recommendations
        """
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Database health
        db_health = SystemHealthService._check_database_health()
        
        # Order metrics
        order_metrics = SystemHealthService._get_order_metrics(last_24h, last_7d)
        
        # User metrics
        user_metrics = SystemHealthService._get_user_metrics()
        
        # Performance metrics
        performance_metrics = SystemHealthService._get_performance_metrics()
        
        # Financial health
        financial_health = SystemHealthService._get_financial_health(last_24h, last_7d)
        
        # Alerts and warnings
        alerts = SystemHealthService._generate_alerts(
            order_metrics, user_metrics, performance_metrics, financial_health
        )
        
        return {
            'status': 'healthy' if len([a for a in alerts if a['severity'] == 'critical']) == 0 else 'degraded',
            'timestamp': now.isoformat(),
            'database': db_health,
            'orders': order_metrics,
            'users': user_metrics,
            'performance': performance_metrics,
            'financial': financial_health,
            'alerts': alerts,
            'recommendations': SystemHealthService._generate_recommendations(alerts)
        }
    
    @staticmethod
    def _check_database_health():
        """Check database connection and performance."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                response_time = 0  # Could measure actual time
            
            # Check for long-running queries (simplified)
            return {
                'status': 'healthy',
                'response_time_ms': response_time,
                'connections': connection.queries_logged if hasattr(connection, 'queries_logged') else 'unknown'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @staticmethod
    def _get_order_metrics(last_24h, last_7d):
        """Get order-related metrics."""
        total_orders = Order.objects.count()
        orders_24h = Order.objects.filter(created_at__gte=last_24h).count()
        orders_7d = Order.objects.filter(created_at__gte=last_7d).count()
        
        # Status breakdown
        status_breakdown = Order.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Overdue orders
        overdue_orders = Order.objects.filter(
            writer_deadline__lt=timezone.now(),
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.SUBMITTED.value,
                OrderStatus.UNDER_EDITING.value
            ]
        ).count()
        
        # Stuck orders (no activity for 48+ hours)
        stuck_threshold = timezone.now() - timedelta(hours=48)
        stuck_orders = Order.objects.filter(
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.SUBMITTED.value
            ],
            updated_at__lt=stuck_threshold
        ).count()
        
        return {
            'total': total_orders,
            'last_24h': orders_24h,
            'last_7d': orders_7d,
            'status_breakdown': {item['status']: item['count'] for item in status_breakdown},
            'overdue': overdue_orders,
            'stuck': stuck_orders,
            'avg_completion_time_hours': SystemHealthService._get_avg_completion_time()
        }
    
    @staticmethod
    def _get_user_metrics():
        """Get user-related metrics."""
        total_users = User.objects.count()
        active_users_30d = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Role breakdown
        role_breakdown = User.objects.values('role').annotate(
            count=Count('id')
        )
        
        # Suspended users
        suspended = User.objects.filter(is_suspended=True).count()
        
        # Writers with issues (use correct related names: strikes / suspensions)
        writers_with_issues = WriterProfile.objects.filter(
            Q(strikes__isnull=False) |
            Q(suspensions__isnull=False)
        ).distinct().count()
        
        return {
            'total': total_users,
            'active_30d': active_users_30d,
            'role_breakdown': {item['role']: item['count'] for item in role_breakdown},
            'suspended': suspended,
            'writers_with_issues': writers_with_issues
        }
    
    @staticmethod
    def _get_performance_metrics():
        """Get system performance metrics."""
        # Cache hit rate (simplified)
        cache_stats = cache.get('system_cache_stats', {})
        
        return {
            'cache_hit_rate': cache_stats.get('hit_rate', 0),
            'avg_response_time_ms': cache_stats.get('avg_response_time', 0),
            'api_requests_24h': cache_stats.get('api_requests_24h', 0)
        }
    
    @staticmethod
    def _get_financial_health(last_24h, last_7d):
        """Get financial health metrics."""
        # Recent payments
        payments_24h = WriterPayment.objects.filter(
            payment_date__gte=last_24h
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        payments_7d = WriterPayment.objects.filter(
            payment_date__gte=last_7d
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Pending fines
        pending_fines = Fine.objects.filter(
            status__in=['active', 'pending']
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        return {
            'payments_24h': {
                'total': float(payments_24h['total'] or 0),
                'count': payments_24h['count']
            },
            'payments_7d': {
                'total': float(payments_7d['total'] or 0),
                'count': payments_7d['count']
            },
            'pending_fines': {
                'total': float(pending_fines['total'] or 0),
                'count': pending_fines['count']
            }
        }
    
    @staticmethod
    def _get_avg_completion_time():
        """Calculate average order completion time."""
        completed_orders = Order.objects.filter(
            status__in=[OrderStatus.COMPLETED.value, OrderStatus.REVIEWED.value],
            created_at__isnull=False,
            updated_at__isnull=False
        )
        
        if not completed_orders.exists():
            return None
        
        # Simplified - would need proper completion timestamp
        return None  # Placeholder
    
    @staticmethod
    def _generate_alerts(order_metrics, user_metrics, performance_metrics, financial_health):
        """Generate alerts based on metrics."""
        alerts = []
        
        # Order alerts
        if order_metrics['overdue'] > 10:
            alerts.append({
                'type': 'orders',
                'severity': 'warning',
                'message': f"{order_metrics['overdue']} orders are overdue",
                'action': 'Review overdue orders'
            })
        
        if order_metrics['stuck'] > 5:
            alerts.append({
                'type': 'orders',
                'severity': 'warning',
                'message': f"{order_metrics['stuck']} orders appear to be stuck",
                'action': 'Check stuck orders'
            })
        
        # User alerts
        if user_metrics['suspended'] > 0:
            alerts.append({
                'type': 'users',
                'severity': 'info',
                'message': f"{user_metrics['suspended']} users are suspended",
                'action': 'Review suspended users'
            })
        
        # Financial alerts
        if financial_health['pending_fines']['total'] > 1000:
            alerts.append({
                'type': 'financial',
                'severity': 'info',
                'message': f"${financial_health['pending_fines']['total']:.2f} in pending fines",
                'action': 'Review pending fines'
            })
        
        return alerts
    
    @staticmethod
    def _generate_recommendations(alerts):
        """Generate recommendations based on alerts."""
        recommendations = []
        
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        if critical_alerts:
            recommendations.append({
                'priority': 'high',
                'message': 'Address critical alerts immediately',
                'actions': [a['action'] for a in critical_alerts]
            })
        
        warning_alerts = [a for a in alerts if a['severity'] == 'warning']
        if warning_alerts:
            recommendations.append({
                'priority': 'medium',
                'message': 'Review and address warning alerts',
                'actions': [a['action'] for a in warning_alerts]
            })
        
        return recommendations

