from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Avg, Sum, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, OrderPricingSnapshot
from order_payments_management.models import OrderPayment
from pricing_configs.models import PricingConfiguration, AdditionalService


class PricingAnalyticsViewSet(viewsets.ViewSet):
    """API for pricing analytics and optimization insights."""
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'], url_path='overview')
    def get_overview(self, request):
        """Get overall pricing analytics overview."""
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get orders with pricing data
        orders = Order.objects.filter(
            created_at__gte=date_from,
            status__in=['completed', 'in_progress', 'pending']
        )
        
        # Calculate average order values
        payments = OrderPayment.objects.filter(
            order__in=orders,
            status='completed'
        )
        
        total_revenue = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        avg_order_value = payments.aggregate(Avg('amount'))['amount__avg'] or 0
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        
        # Get pricing snapshots if available
        # Note: JSONField queries need special handling - calculate from Python
        snapshots = OrderPricingSnapshot.objects.filter(
            order__in=orders
        ).values('pricing_data')
        
        base_prices = []
        final_totals = []
        for snapshot in snapshots:
            pricing_data = snapshot.get('pricing_data', {})
            if isinstance(pricing_data, dict):
                if 'base_price' in pricing_data:
                    base_prices.append(float(pricing_data['base_price']))
                if 'final_total' in pricing_data:
                    final_totals.append(float(pricing_data['final_total']))
        
        avg_base_price = sum(base_prices) / len(base_prices) if base_prices else 0
        avg_final_total = sum(final_totals) / len(final_totals) if final_totals else 0
        
        return Response({
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value),
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'avg_base_price': float(avg_base_price),
            'avg_final_total': float(avg_final_total),
            'conversion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
        })
    
    @action(detail=False, methods=['get'], url_path='trends')
    def get_trends(self, request):
        """Get pricing trends over time."""
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get daily revenue and order counts
        payments = OrderPayment.objects.filter(
            order__created_at__gte=date_from,
            status='completed'
        ).annotate(
            date=TruncDate('order__created_at')
        ).values('date').annotate(
            revenue=Sum('amount'),
            order_count=Count('order', distinct=True),
            avg_order_value=Avg('amount')
        ).order_by('date')
        
        trends = []
        for item in payments:
            trends.append({
                'date': item['date'].isoformat() if item['date'] else None,
                'revenue': float(item['revenue'] or 0),
                'order_count': item['order_count'],
                'avg_order_value': float(item['avg_order_value'] or 0),
            })
        
        return Response(trends)
    
    @action(detail=False, methods=['get'], url_path='service-breakdown')
    def get_service_breakdown(self, request):
        """Get pricing breakdown by service type."""
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        orders = Order.objects.filter(
            created_at__gte=date_from,
            status__in=['completed', 'in_progress']
        )
        
        # Group by service type
        # Get payments separately and join
        payments = OrderPayment.objects.filter(
            order__in=orders,
            status='completed'
        ).select_related('order')
        
        service_revenue = {}
        for payment in payments:
            service_type = payment.order.service_type or 'Unknown'
            if service_type not in service_revenue:
                service_revenue[service_type] = {'total': 0, 'count': 0}
            service_revenue[service_type]['total'] += float(payment.amount)
            service_revenue[service_type]['count'] += 1
        
        # Also get order counts by service type
        service_counts = orders.values('service_type').annotate(
            count=Count('id')
        )
        
        service_stats = {}
        for item in service_counts:
            service_type = item['service_type'] or 'Unknown'
            service_stats[service_type] = {'order_count': item['count']}
        
        # Merge revenue data
        breakdown = []
        for service_type, data in service_stats.items():
            revenue_data = service_revenue.get(service_type, {'total': 0, 'count': 0})
            breakdown.append({
                'service_type': service_type,
                'order_count': data['order_count'],
                'total_revenue': revenue_data['total'],
                'avg_revenue': revenue_data['total'] / revenue_data['count'] if revenue_data['count'] > 0 else 0,
            })
        
        # Sort by total revenue
        breakdown.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        return Response(breakdown)
    
    @action(detail=False, methods=['get'], url_path='academic-level-breakdown')
    def get_academic_level_breakdown(self, request):
        """Get pricing breakdown by academic level."""
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        orders = Order.objects.filter(
            created_at__gte=date_from,
            status__in=['completed', 'in_progress']
        )
        
        # Group by academic level - similar approach as service breakdown
        payments = OrderPayment.objects.filter(
            order__in=orders,
            status='completed'
        ).select_related('order', 'order__academic_level')
        
        level_revenue = {}
        for payment in payments:
            level_name = payment.order.academic_level.name if payment.order.academic_level else 'Unknown'
            if level_name not in level_revenue:
                level_revenue[level_name] = {'total': 0, 'count': 0}
            level_revenue[level_name]['total'] += float(payment.amount)
            level_revenue[level_name]['count'] += 1
        
        # Get order counts by academic level
        level_counts = orders.values('academic_level__name').annotate(
            count=Count('id')
        )
        
        level_stats = {}
        for item in level_counts:
            level_name = item['academic_level__name'] or 'Unknown'
            level_stats[level_name] = {'order_count': item['count']}
        
        # Merge revenue data
        breakdown = []
        for level_name, data in level_stats.items():
            revenue_data = level_revenue.get(level_name, {'total': 0, 'count': 0})
            breakdown.append({
                'academic_level': level_name,
                'order_count': data['order_count'],
                'total_revenue': revenue_data['total'],
                'avg_revenue': revenue_data['total'] / revenue_data['count'] if revenue_data['count'] > 0 else 0,
            })
        
        # Sort by total revenue
        breakdown.sort(key=lambda x: x['total_revenue'], reverse=True)
        
        return Response(breakdown)
    
    @action(detail=False, methods=['get'], url_path='pricing-configs')
    def get_pricing_configs(self, request):
        """Get active pricing configurations."""
        configs = PricingConfiguration.objects.all().select_related('website')
        
        config_list = []
        for config in configs:
            config_list.append({
                'id': config.id,
                'website': config.website.name if config.website else 'N/A',
                'base_price_per_page': float(config.base_price_per_page),
                'created_at': config.created_at.isoformat() if config.created_at else None,
                'updated_at': config.updated_at.isoformat() if config.updated_at else None,
            })
        
        return Response(config_list)
    
    @action(detail=False, methods=['get'], url_path='additional-services')
    def get_additional_services(self, request):
        """Get additional service pricing and usage."""
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        services = AdditionalService.objects.filter(is_active=True)
        
        service_list = []
        for service in services:
            # Count orders using this service
            orders_with_service = Order.objects.filter(
                created_at__gte=date_from,
                additional_services=service
            ).count()
            
            service_list.append({
                'id': service.id,
                'name': service.name,
                'price': float(service.price),
                'usage_count': orders_with_service,
            })
        
        return Response(service_list)

