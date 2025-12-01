"""
Enhanced analytics service for admin dashboard.
Provides deeper insights and trend analysis.
"""
from django.db.models import Count, Sum, Avg, Q, F, DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Any

from orders.models import Order
from orders.order_enums import OrderStatus
from users.models import User
from writer_management.models import WriterProfile
from writer_wallet.models import WriterPayment


class EnhancedAnalyticsService:
    """Service for enhanced analytics and insights."""
    
    @staticmethod
    def get_performance_insights(days=30):
        """
        Get performance insights and trends.
        
        Args:
            days: Number of days to analyze (default: 30)
            
        Returns:
            dict: Performance insights including trends, predictions, and recommendations
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Order completion trends
        orders = Order.objects.filter(created_at__gte=start_date)
        
        # Daily order trends
        daily_trends = orders.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            total=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'reviewed'])),
            revenue=Sum('total_price', filter=Q(is_paid=True), output_field=DecimalField())
        ).order_by('day')
        
        # Average order completion time (simplified)
        completed_orders = orders.filter(
            status__in=['completed', 'reviewed'],
            created_at__isnull=False,
            updated_at__isnull=False
        )
        
        # Writer performance metrics
        # Use calculated_earnings instead of total_earnings to avoid conflict with model field
        writer_performance = WriterProfile.objects.annotate(
            completed_count=Count('user__orders_as_writer', filter=Q(
                user__orders_as_writer__status__in=['completed', 'reviewed'],
                user__orders_as_writer__created_at__gte=start_date
            )),
            calculated_earnings=Sum('user__orders_as_writer__writer_compensation', filter=Q(
                user__orders_as_writer__status__in=['completed', 'reviewed'],
                user__orders_as_writer__created_at__gte=start_date
            ), output_field=DecimalField())
        ).filter(completed_count__gt=0).order_by('-completed_count')[:10]
        
        # Client retention metrics
        client_metrics = User.objects.filter(
            role='client',
            orders_as_client__created_at__gte=start_date
        ).annotate(
            order_count=Count('orders_as_client'),
            total_spent=Sum('orders_as_client__total_price', filter=Q(
                orders_as_client__is_paid=True
            ), output_field=DecimalField()),
            repeat_orders=Count('orders_as_client', filter=Q(
                orders_as_client__created_at__gte=start_date
            )) - 1  # Subtract 1 to get repeat count
        ).filter(order_count__gt=0)
        
        # Calculate retention rate (clients with 2+ orders)
        total_clients = client_metrics.count()
        repeat_clients = client_metrics.filter(repeat_orders__gt=0).count()
        retention_rate = (repeat_clients / total_clients * 100) if total_clients > 0 else 0
        
        # Revenue trends
        revenue_trends = orders.filter(
            is_paid=True
        ).annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            revenue=Sum('total_price', output_field=DecimalField()),
            count=Count('id')
        ).order_by('day')
        
        # Predictions (simple linear trend)
        if len(revenue_trends) >= 7:
            recent_revenue = [float(item['revenue'] or 0) for item in revenue_trends[-7:]]
            avg_recent = sum(recent_revenue) / len(recent_revenue)
            predicted_next_week = avg_recent * 7
        else:
            predicted_next_week = 0
        
        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily_trends': [
                {
                    'date': item['day'].isoformat() if item['day'] else None,
                    'total_orders': item['total'],
                    'completed_orders': item['completed'],
                    'revenue': float(item['revenue'] or 0),
                    'completion_rate': (item['completed'] / item['total'] * 100) if item['total'] > 0 else 0
                }
                for item in daily_trends
            ],
            'writer_performance': [
                {
                    'writer_id': wp.user.id if wp.user else None,
                    'writer_username': wp.user.username if wp.user else 'Unknown',
                    'completed_orders': wp.completed_count,
                    'total_earnings': float(wp.calculated_earnings or 0)
                }
                for wp in writer_performance
            ],
            'client_metrics': {
                'total_active_clients': total_clients,
                'repeat_clients': repeat_clients,
                'retention_rate': round(retention_rate, 2),
                'avg_orders_per_client': round(
                    sum(c.order_count for c in client_metrics) / total_clients if total_clients > 0 else 0,
                    2
                ),
                'avg_spend_per_client': round(
                    sum(float(c.total_spent or 0) for c in client_metrics) / total_clients if total_clients > 0 else 0,
                    2
                )
            },
            'revenue_trends': [
                {
                    'date': item['day'].isoformat() if item['day'] else None,
                    'revenue': float(item['revenue'] or 0),
                    'order_count': item['count']
                }
                for item in revenue_trends
            ],
            'predictions': {
                'predicted_revenue_next_week': round(predicted_next_week, 2),
                'confidence': 'medium' if len(revenue_trends) >= 7 else 'low'
            },
            'insights': EnhancedAnalyticsService._generate_insights(
                daily_trends, revenue_trends, retention_rate, total_clients
            )
        }
    
    @staticmethod
    def _generate_insights(daily_trends, revenue_trends, retention_rate, total_clients):
        """Generate actionable insights from metrics."""
        insights = []
        
        # Trend analysis
        if len(daily_trends) >= 7:
            recent_avg = sum(item['total_orders'] for item in daily_trends[-7:]) / 7
            earlier_avg = sum(item['total_orders'] for item in daily_trends[:7]) / 7 if len(daily_trends) >= 14 else recent_avg
            
            if recent_avg > earlier_avg * 1.1:
                insights.append({
                    'type': 'positive',
                    'title': 'Growing Order Volume',
                    'message': f'Order volume has increased by {round((recent_avg / earlier_avg - 1) * 100, 1)}% compared to earlier period.',
                    'action': 'Consider scaling writer capacity to maintain quality.'
                })
            elif recent_avg < earlier_avg * 0.9:
                insights.append({
                    'type': 'warning',
                    'title': 'Declining Order Volume',
                    'message': f'Order volume has decreased by {round((1 - recent_avg / earlier_avg) * 100, 1)}% compared to earlier period.',
                    'action': 'Review marketing efforts and client engagement strategies.'
                })
        
        # Retention insights
        if retention_rate < 30:
            insights.append({
                'type': 'warning',
                'title': 'Low Client Retention',
                'message': f'Only {round(retention_rate, 1)}% of clients are repeat customers.',
                'action': 'Focus on improving order quality and client satisfaction to increase retention.'
            })
        elif retention_rate > 60:
            insights.append({
                'type': 'positive',
                'title': 'Strong Client Retention',
                'message': f'{round(retention_rate, 1)}% of clients are repeat customers.',
                'action': 'Maintain current quality standards and consider loyalty programs.'
            })
        
        # Revenue insights
        if len(revenue_trends) >= 7:
            recent_revenue = sum(float(item['revenue'] or 0) for item in revenue_trends[-7:])
            earlier_revenue = sum(float(item['revenue'] or 0) for item in revenue_trends[:7]) if len(revenue_trends) >= 14 else recent_revenue
            
            if recent_revenue > earlier_revenue * 1.15:
                insights.append({
                    'type': 'positive',
                    'title': 'Strong Revenue Growth',
                    'message': 'Revenue has shown significant growth in recent days.',
                    'action': 'Continue current strategies and monitor for scaling opportunities.'
                })
        
        return insights
    
    @staticmethod
    def get_comparative_analytics(period1_days=30, period2_days=30):
        """
        Compare two time periods.
        
        Args:
            period1_days: Days for first period (default: 30)
            period2_days: Days for second period (default: 30)
            
        Returns:
            dict: Comparative analytics
        """
        now = timezone.now()
        period1_end = now
        period1_start = now - timedelta(days=period1_days)
        period2_end = period1_start
        period2_start = period2_end - timedelta(days=period2_days)
        
        def get_period_metrics(start, end):
            orders = Order.objects.filter(created_at__gte=start, created_at__lt=end)
            return {
                'total_orders': orders.count(),
                'completed_orders': orders.filter(status__in=['completed', 'reviewed']).count(),
                'revenue': float(orders.filter(is_paid=True).aggregate(
                    total=Sum('total_price', output_field=DecimalField())
                )['total'] or 0),
                'new_clients': User.objects.filter(
                    role='client',
                    date_joined__gte=start,
                    date_joined__lt=end
                ).count()
            }
        
        period1 = get_period_metrics(period1_start, period1_end)
        period2 = get_period_metrics(period2_start, period2_end)
        
        def calculate_change(current, previous):
            if previous == 0:
                return {'percent': 0, 'absolute': current}
            return {
                'percent': round(((current - previous) / previous) * 100, 2),
                'absolute': round(current - previous, 2)
            }
        
        return {
            'period1': {
                'start': period1_start.isoformat(),
                'end': period1_end.isoformat(),
                'metrics': period1
            },
            'period2': {
                'start': period2_start.isoformat(),
                'end': period2_end.isoformat(),
                'metrics': period2
            },
            'comparison': {
                'orders': calculate_change(period1['total_orders'], period2['total_orders']),
                'completed': calculate_change(period1['completed_orders'], period2['completed_orders']),
                'revenue': calculate_change(period1['revenue'], period2['revenue']),
                'new_clients': calculate_change(period1['new_clients'], period2['new_clients'])
            }
        }

