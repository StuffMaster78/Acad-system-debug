"""
Service for generating dashboard metrics for admin dashboard.
Provides role-aware, tenant-aware metrics with caching.
"""
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Any, Optional
from decimal import Decimal

from orders.models import Order
from orders.order_enums import OrderStatus
from users.models import User
from tickets.models import Ticket
from communications.models import CommunicationMessage
from pricing_configs.models import AdditionalService


class DashboardMetricsService:
    """
    Service for generating comprehensive dashboard metrics.
    Role-aware and tenant-aware (website-scoped).
    """
    
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def get_cache_key(user, key_suffix: str) -> str:
        """Generate cache key for user-specific metrics."""
        website_id = getattr(user, 'website_id', None) or 'all'
        role = getattr(user, 'role', 'unknown')
        return f"dashboard_metrics_{role}_{website_id}_{key_suffix}"
    
    @staticmethod
    def get_summary(user) -> Dict[str, Any]:
        """
        Get summary metrics for dashboard.
        Role-aware: Admin sees all, Client sees only their orders, etc.
        """
        cache_key = DashboardMetricsService.get_cache_key(user, "summary")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        website = getattr(user, 'website', None)
        role = getattr(user, 'role', 'client')
        
        # Base queryset - no website filtering for superadmin and admin
        order_qs = Order.objects.all()
        # Both superadmin and admin see all orders (no website filtering)
        if role not in ['superadmin', 'admin']:
            if website:
                order_qs = order_qs.filter(website=website)
        
        # Role-based filtering
        if role == 'client':
            order_qs = order_qs.filter(client=user)
        elif role == 'writer':
            order_qs = order_qs.filter(assigned_writer=user)
        elif role == 'editor':
            # Editors see orders they're reviewing
            try:
                from editor_management.models import EditorTaskAssignment
                editor_tasks = EditorTaskAssignment.objects.filter(
                    assigned_editor__user=user
                ).values_list('order_id', flat=True)
                if editor_tasks.exists():
                    order_qs = order_qs.filter(id__in=list(editor_tasks))
                else:
                    order_qs = order_qs.none()
            except Exception:
                order_qs = order_qs.none()
        # Admin/Superadmin see all orders (no additional filtering)
        
        # Orders by status - combined query
        orders_by_status = order_qs.values('status').annotate(
            count=Count('id')
        )
        status_counts = {item['status']: item['count'] for item in orders_by_status}
        total_orders = sum(item['count'] for item in orders_by_status)
        
        # Revenue metrics and order counts - combined into single aggregation
        recent_cutoff = timezone.now() - timedelta(days=7)
        
        # Calculate paid/unpaid orders correctly
        # Paid orders: orders where is_paid=True
        # Unpaid orders: orders where is_paid=False OR is_paid is None
        paid_orders_qs = order_qs.filter(is_paid=True)
        unpaid_orders_qs = order_qs.filter(Q(is_paid=False) | Q(is_paid__isnull=True))
        recent_orders_qs = order_qs.filter(created_at__gte=recent_cutoff)
        
        order_stats = order_qs.aggregate(
            total_revenue=Sum('total_price', filter=Q(is_paid=True), output_field=DecimalField()),
        )
        
        # Get counts separately to ensure accuracy
        paid_orders_count = paid_orders_qs.count()
        unpaid_orders_count = unpaid_orders_qs.count()
        recent_orders_count = recent_orders_qs.count()
        
        total_revenue = order_stats['total_revenue'] or Decimal('0.00')
        
        # Tickets (if applicable) - combined queries
        ticket_qs = Ticket.objects.all()
        # Both superadmin and admin see all tickets (no website filtering)
        if role not in ['superadmin', 'admin']:
            if website:
                ticket_qs = ticket_qs.filter(website=website)
        if role == 'client':
            ticket_qs = ticket_qs.filter(client=user)
        
        # Combined ticket statistics
        ticket_stats = ticket_qs.aggregate(
            total_tickets=Count('id'),
            open_tickets=Count('id', filter=Q(status__in=['open', 'pending'])),
            closed_tickets=Count('id', filter=Q(status='closed'))
        )
        total_tickets = ticket_stats['total_tickets'] or 0
        open_tickets = ticket_stats['open_tickets'] or 0
        closed_tickets = ticket_stats['closed_tickets'] or 0
        
        # Additional metrics for admin/superadmin dashboard
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Orders in progress (active work states)
        orders_in_progress = order_qs.filter(
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.ASSIGNED.value,
                OrderStatus.UNDER_EDITING.value,
                OrderStatus.SUBMITTED.value,
                OrderStatus.UNDER_REVIEW.value,
            ]
        ).count()
        
        # Orders on revision
        orders_on_revision = order_qs.filter(
            status__in=[
                OrderStatus.ON_REVISION.value,
                OrderStatus.REVISION_REQUESTED.value,
                OrderStatus.REVISED.value,
            ]
        ).count()
        
        # Disputed orders
        disputed_orders = order_qs.filter(status=OrderStatus.DISPUTED.value).count()
        
        # Amount paid today - use OrderPayment model
        try:
            from order_payments_management.models import OrderPayment
            # Get payments confirmed today (use confirmed_at if available, otherwise created_at)
            payments_today = OrderPayment.objects.filter(
                status__in=['completed', 'succeeded'],
            ).filter(
                Q(confirmed_at__gte=today_start, confirmed_at__lt=today_end) |
                Q(confirmed_at__isnull=True, created_at__gte=today_start, created_at__lt=today_end)
            )
            amount_paid_today = payments_today.aggregate(
                total=Sum('amount', output_field=DecimalField())
            )['total'] or Decimal('0.00')
            
            # Income for last 2 weeks
            two_weeks_ago = timezone.now() - timedelta(days=14)
            payments_2weeks = OrderPayment.objects.filter(
                status__in=['completed', 'succeeded'],
            ).filter(
                Q(confirmed_at__gte=two_weeks_ago) |
                Q(confirmed_at__isnull=True, created_at__gte=two_weeks_ago)
            )
            income_2weeks = payments_2weeks.aggregate(
                total=Sum('amount', output_field=DecimalField())
            )['total'] or Decimal('0.00')
            
            # Income for this week (last 7 days)
            week_start = timezone.now() - timedelta(days=7)
            payments_this_week = OrderPayment.objects.filter(
                status__in=['completed', 'succeeded'],
            ).filter(
                Q(confirmed_at__gte=week_start) |
                Q(confirmed_at__isnull=True, created_at__gte=week_start)
            )
            income_this_week = payments_this_week.aggregate(
                total=Sum('amount', output_field=DecimalField())
            )['total'] or Decimal('0.00')
            
            # Income for current month
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            payments_monthly = OrderPayment.objects.filter(
                status__in=['completed', 'succeeded'],
            ).filter(
                Q(confirmed_at__gte=month_start) |
                Q(confirmed_at__isnull=True, created_at__gte=month_start)
            )
            income_monthly = payments_monthly.aggregate(
                total=Sum('amount', output_field=DecimalField())
            )['total'] or Decimal('0.00')
        except ImportError:
            # Fallback to order-based calculation if OrderPayment is not available
            amount_paid_today = Decimal('0.00')
            two_weeks_ago = timezone.now() - timedelta(days=14)
            income_2weeks = order_qs.filter(
                is_paid=True,
                updated_at__gte=two_weeks_ago
            ).aggregate(
                total=Sum('total_price', output_field=DecimalField())
            )['total'] or Decimal('0.00')
            week_start = timezone.now() - timedelta(days=7)
            income_this_week = order_qs.filter(
                is_paid=True,
                updated_at__gte=week_start
            ).aggregate(
                total=Sum('total_price', output_field=DecimalField())
            )['total'] or Decimal('0.00')
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            income_monthly = order_qs.filter(
                is_paid=True,
                updated_at__gte=month_start
            ).aggregate(
                total=Sum('total_price', output_field=DecimalField())
            )['total'] or Decimal('0.00')
        
        summary = {
            'total_orders': total_orders,
            'orders_by_status': status_counts,
            'total_revenue': float(total_revenue),
            'paid_orders_count': paid_orders_count,
            'unpaid_orders_count': unpaid_orders_count,
            'recent_orders_count': recent_orders_count,  # Last 7 days
            'total_tickets': total_tickets,
            'open_tickets_count': open_tickets,
            'closed_tickets_count': closed_tickets,
            # New metrics for admin/superadmin
            'orders_in_progress': orders_in_progress,
            'orders_on_revision': orders_on_revision,
            'disputed_orders': disputed_orders,
            'amount_paid_today': float(amount_paid_today),
            'income_this_week': float(income_this_week),
            'income_2weeks': float(income_2weeks),
            'income_monthly': float(income_monthly),
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, summary, DashboardMetricsService.CACHE_TIMEOUT)
        return summary
    
    @staticmethod
    def get_yearly_orders(user, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get yearly order counts and revenue.
        Returns list of years with order counts and revenue.
        """
        if year is None:
            year = timezone.now().year
        
        cache_key = DashboardMetricsService.get_cache_key(user, f"yearly_{year}")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        website = getattr(user, 'website', None)
        role = getattr(user, 'role', 'client')
        
        order_qs = Order.objects.filter(created_at__year=year)
        # Both superadmin and admin see all orders (no website filtering)
        if role not in ['superadmin', 'admin']:
            if website:
                order_qs = order_qs.filter(website=website)
        
        if role == 'client':
            order_qs = order_qs.filter(client=user)
        elif role == 'writer':
            order_qs = order_qs.filter(assigned_writer=user)
        
        # Group by month
        monthly_data = order_qs.annotate(
            month_start=TruncMonth('created_at')
        ).values('month_start').annotate(
            order_count=Count('id'),
            revenue=Sum('total_price', filter=Q(is_paid=True), output_field=DecimalField())
        ).order_by('month_start')
        
        month_lookup = {}
        for item in monthly_data:
            month_dt = item.get('month_start')
            if month_dt:
                month_lookup[month_dt.month] = item
        
        # Format for frontend (ensure all 12 months)
        result = []
        for month_num in range(1, 13):
            month_data = month_lookup.get(month_num)
            order_count = month_data.get('order_count', 0) if month_data else 0
            revenue_value = month_data.get('revenue', Decimal('0.00')) if month_data else Decimal('0.00')
            result.append({
                'month': month_num,
                'month_name': datetime(2000, month_num, 1).strftime('%B'),
                'order_count': order_count,
                'revenue': float(revenue_value or Decimal('0.00')),
            })
        
        cache.set(cache_key, result, DashboardMetricsService.CACHE_TIMEOUT)
        return result
    
    @staticmethod
    def get_yearly_earnings(user, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get yearly earnings breakdown.
        Same as yearly orders but focused on revenue.
        """
        return DashboardMetricsService.get_yearly_orders(user, year)
    
    @staticmethod
    def get_monthly_orders(user, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get monthly order breakdown (daily).
        """
        if year is None:
            year = timezone.now().year
        if month is None:
            month = timezone.now().month
        
        cache_key = DashboardMetricsService.get_cache_key(user, f"monthly_{year}_{month}")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        website = getattr(user, 'website', None)
        role = getattr(user, 'role', 'client')
        
        order_qs = Order.objects.filter(
            created_at__year=year,
            created_at__month=month
        )
        # Both superadmin and admin see all orders (no website filtering)
        if role not in ['superadmin', 'admin']:
            if website:
                order_qs = order_qs.filter(website=website)
        
        if role == 'client':
            order_qs = order_qs.filter(client=user)
        elif role == 'writer':
            order_qs = order_qs.filter(assigned_writer=user)
        
        # Group by day
        daily_data = order_qs.annotate(
            day_start=TruncDay('created_at')
        ).values('day_start').annotate(
            order_count=Count('id'),
            revenue=Sum('total_price', filter=Q(is_paid=True), output_field=DecimalField())
        ).order_by('day_start')
        
        day_lookup = {}
        for item in daily_data:
            day_dt = item.get('day_start')
            if day_dt:
                day_lookup[day_dt.day] = item
        
        days_in_month = calendar.monthrange(year, month)[1]
        result = []
        for day in range(1, days_in_month + 1):
            day_data = day_lookup.get(day)
            revenue_value = day_data.get('revenue', Decimal('0.00')) if day_data else Decimal('0.00')
            result.append({
                'day': day,
                'order_count': day_data.get('order_count', 0) if day_data else 0,
                'revenue': float(revenue_value or Decimal('0.00')),
            })
        
        cache.set(cache_key, result, DashboardMetricsService.CACHE_TIMEOUT)
        return result
    
    @staticmethod
    def get_service_revenue(user, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get revenue breakdown by service type.
        """
        cache_key = DashboardMetricsService.get_cache_key(user, f"service_revenue_{days}")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        website = getattr(user, 'website', None)
        role = getattr(user, 'role', 'client')
        
        cutoff = timezone.now() - timedelta(days=days)
        
        order_qs = Order.objects.filter(
            created_at__gte=cutoff,
            is_paid=True
        )
        # Both superadmin and admin see all orders (no website filtering)
        if role not in ['superadmin', 'admin']:
            if website:
                order_qs = order_qs.filter(website=website)
        
        if role == 'client':
            order_qs = order_qs.filter(client=user)
        elif role == 'writer':
            order_qs = order_qs.filter(assigned_writer=user)
        
        # Revenue by paper type
        paper_type_revenue = order_qs.values('paper_type__name').annotate(
            revenue=Sum('total_price', output_field=DecimalField()),
            count=Count('id')
        )
        
        # Revenue by additional services
        # For ManyToMany relationships, we need to query from the service side
        # Get the order IDs that match our filters
        order_ids = list(order_qs.values_list('id', flat=True))
        
        if not order_ids:
            # No orders match, return empty service revenue
            service_revenue = []
        else:
            # Query services that are related to these orders
            # Filter by website if not superadmin/admin
            service_qs = AdditionalService.objects.filter(orders__id__in=order_ids)
            if role not in ['superadmin', 'admin'] and website:
                service_qs = service_qs.filter(website=website)
            
            service_revenue = service_qs.annotate(
                revenue=Sum('orders__total_price', output_field=DecimalField()),
                count=Count('orders__id', distinct=True)
            ).values('service_name', 'revenue', 'count')
        
        result = {
            'by_paper_type': [
                {
                    'name': item['paper_type__name'] or 'Unknown',
                    'revenue': float(item.get('revenue', Decimal('0.00'))),
                    'order_count': item.get('count', 0),
                }
                for item in paper_type_revenue
            ],
            'by_service': [
                {
                    'name': item['service_name'] or 'Unknown',
                    'revenue': float(item.get('revenue', Decimal('0.00'))),
                    'order_count': item.get('count', 0),
                }
                for item in service_revenue
            ],
        }
        
        cache.set(cache_key, result, DashboardMetricsService.CACHE_TIMEOUT)
        return result
    
    @staticmethod
    def get_payment_status_breakdown(user) -> Dict[str, Any]:
        """
        Get payment status breakdown.
        """
        cache_key = DashboardMetricsService.get_cache_key(user, "payment_status")
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        
        website = getattr(user, 'website', None)
        role = getattr(user, 'role', 'client')
        
        order_qs = Order.objects.all()
        # Both superadmin and admin see all orders (no website filtering)
        if role not in ['superadmin', 'admin']:
            if website:
                order_qs = order_qs.filter(website=website)
        
        if role == 'client':
            order_qs = order_qs.filter(client=user)
        elif role == 'writer':
            order_qs = order_qs.filter(assigned_writer=user)
        
        payment_data = order_qs.values('is_paid').annotate(
            count=Count('id'),
            total_revenue=Sum('total_price', output_field=DecimalField())
        )
        
        paid_count = next(
            (item['count'] for item in payment_data if item['is_paid']),
            0
        )
        unpaid_count = next(
            (item['count'] for item in payment_data if not item['is_paid']),
            0
        )
        
        paid_revenue = next(
            (float(item['total_revenue']) for item in payment_data if item['is_paid']),
            0.0
        )
        
        result = {
            'paid': {
                'count': paid_count,
                'revenue': paid_revenue,
            },
            'unpaid': {
                'count': unpaid_count,
                'revenue': 0.0,  # Unpaid orders don't contribute to revenue
            },
        }
        
        cache.set(cache_key, result, DashboardMetricsService.CACHE_TIMEOUT)
        return result

