"""
Financial Overview API endpoints for admin dashboard.
Provides comprehensive financial analytics including earnings, expenses, and net revenue.
"""
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from orders.models import Order
from special_orders.models import SpecialOrder
from class_management.models import ClassBundle
from order_payments_management.models import OrderPayment
from writer_wallet.models import ScheduledWriterPayment, PaymentSchedule
from writer_management.models.tipping import Tip
from websites.models import Website


class FinancialOverviewViewSet(ViewSet):
    """
    Financial overview endpoints for admin dashboard.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get comprehensive financial overview including:
        - Total earnings (orders, special orders, classes)
        - Writer payments (expenses)
        - Net revenue
        - Breakdown by period
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Check admin access
        if not (request.user.is_staff or request.user.role in ['admin', 'superadmin']):
            return Response({"error": "Unauthorized"}, status=403)
        
        # Get date range filters
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        website_id = request.query_params.get('website_id')
        
        # Build base querysets
        orders_qs = Order.objects.filter(is_paid=True)
        special_orders_qs = SpecialOrder.objects.filter(is_paid=True)
        class_bundles_qs = ClassBundle.objects.filter(is_paid=True)
        writer_payments_qs = ScheduledWriterPayment.objects.filter(status='Paid')
        
        if website_id:
            orders_qs = orders_qs.filter(website_id=website_id)
            special_orders_qs = special_orders_qs.filter(website_id=website_id)
            class_bundles_qs = class_bundles_qs.filter(website_id=website_id)
            writer_payments_qs = writer_payments_qs.filter(website_id=website_id)
        
        if date_from:
            orders_qs = orders_qs.filter(paid_at__gte=date_from)
            special_orders_qs = special_orders_qs.filter(paid_at__gte=date_from)
            class_bundles_qs = class_bundles_qs.filter(paid_at__gte=date_from)
            writer_payments_qs = writer_payments_qs.filter(payment_date__gte=date_from)
        
        if date_to:
            orders_qs = orders_qs.filter(paid_at__lte=date_to)
            special_orders_qs = special_orders_qs.filter(paid_at__lte=date_to)
            class_bundles_qs = class_bundles_qs.filter(paid_at__lte=date_to)
            writer_payments_qs = writer_payments_qs.filter(payment_date__lte=date_to)
        
        # Calculate earnings
        # Standard Orders
        order_payments = OrderPayment.objects.filter(
            order__in=orders_qs,
            status='completed'
        )
        total_order_revenue = order_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Special Orders
        special_order_revenue = special_orders_qs.aggregate(
            total=Sum('total_cost')
        )['total'] or Decimal('0.00')
        
        # Class Bundles
        class_revenue = class_bundles_qs.aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0.00')
        
        # Total Revenue
        total_revenue = total_order_revenue + special_order_revenue + class_revenue
        
        # Calculate Expenses (Writer Payments)
        total_writer_payments = writer_payments_qs.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Tips (these are expenses as they're paid to writers)
        tips_qs = Tip.objects.filter(
            payment_status='completed',
            website_id=website_id if website_id else None
        )
        if date_from:
            tips_qs = tips_qs.filter(sent_at__gte=date_from)
        if date_to:
            tips_qs = tips_qs.filter(sent_at__lte=date_to)
        
        total_tips_paid = tips_qs.aggregate(
            total=Sum('writer_earning')
        )['total'] or Decimal('0.00')
        
        # Total Expenses
        total_expenses = total_writer_payments + total_tips_paid
        
        # Net Revenue
        net_revenue = total_revenue - total_expenses
        
        # Get period breakdown (last 12 months)
        now = timezone.now()
        period_breakdown = []
        for i in range(12):
            month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_orders = OrderPayment.objects.filter(
                order__is_paid=True,
                status='completed',
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            month_order_revenue = month_orders.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            month_special = SpecialOrder.objects.filter(
                is_paid=True,
                paid_at__gte=month_start,
                paid_at__lte=month_end
            )
            month_special_revenue = month_special.aggregate(total=Sum('total_cost'))['total'] or Decimal('0.00')
            
            month_classes = ClassBundle.objects.filter(
                is_paid=True,
                paid_at__gte=month_start,
                paid_at__lte=month_end
            )
            month_class_revenue = month_classes.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
            
            month_writer_payments = ScheduledWriterPayment.objects.filter(
                status='Paid',
                payment_date__gte=month_start,
                payment_date__lte=month_end
            )
            month_expenses = month_writer_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            period_breakdown.append({
                'period': month_start.strftime('%Y-%m'),
                'month': month_start.strftime('%B %Y'),
                'revenue': {
                    'orders': float(month_order_revenue),
                    'special_orders': float(month_special_revenue),
                    'classes': float(month_class_revenue),
                    'total': float(month_order_revenue + month_special_revenue + month_class_revenue),
                },
                'expenses': {
                    'writer_payments': float(month_expenses),
                    'total': float(month_expenses),
                },
                'net_revenue': float(
                    (month_order_revenue + month_special_revenue + month_class_revenue) - month_expenses
                ),
            })
        
        return Response({
            'summary': {
                'total_revenue': float(total_revenue),
                'revenue_breakdown': {
                    'orders': float(total_order_revenue),
                    'special_orders': float(special_order_revenue),
                    'classes': float(class_revenue),
                },
                'total_expenses': float(total_expenses),
                'expenses_breakdown': {
                    'writer_payments': float(total_writer_payments),
                    'tips': float(total_tips_paid),
                },
                'net_revenue': float(net_revenue),
                'profit_margin': float((net_revenue / total_revenue * 100) if total_revenue > 0 else 0),
            },
            'period_breakdown': period_breakdown,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'website_id': website_id,
            }
        })
    
    @action(detail=False, methods=['get'], url_path='all-payments')
    def all_payments(self, request):
        """
        Get all writer payments from system start, with full details.
        """
        if not (request.user.is_staff or request.user.role in ['admin', 'superadmin']):
            return Response({"error": "Unauthorized"}, status=403)
        
        website_id = request.query_params.get('website_id')
        writer_id = request.query_params.get('writer_id')
        status_filter = request.query_params.get('status')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        payments_qs = ScheduledWriterPayment.objects.select_related(
            'writer_wallet__writer__user',
            'batch',
            'website'
        ).prefetch_related('orders__order')
        
        if website_id:
            payments_qs = payments_qs.filter(website_id=website_id)
        if writer_id:
            payments_qs = payments_qs.filter(writer_wallet__writer_id=writer_id)
        if status_filter:
            payments_qs = payments_qs.filter(status=status_filter)
        if date_from:
            payments_qs = payments_qs.filter(payment_date__gte=date_from)
        if date_to:
            payments_qs = payments_qs.filter(payment_date__lte=date_to)
        
        payments_data = []
        for payment in payments_qs.order_by('-payment_date'):
            order_records = payment.orders.all()
            order_count = order_records.count()
            
            payments_data.append({
                'id': payment.id,
                'payment_id': payment.reference_code,
                'writer': {
                    'id': payment.writer_wallet.writer.id,
                    'name': payment.writer_wallet.writer.user.get_full_name() or payment.writer_wallet.writer.user.username,
                    'email': payment.writer_wallet.writer.user.email,
                    'registration_id': payment.writer_wallet.writer.registration_id,
                },
                'number_of_orders': order_count,
                'amount': float(payment.amount),
                'tips': 0.00,  # Will be calculated if needed
                'fines': 0.00,  # Will be calculated if needed
                'total_earnings': float(payment.amount),
                'date': payment.payment_date.isoformat() if payment.payment_date else None,
                'status': payment.status,
                'type': payment.batch.schedule_type if payment.batch else 'Manual',
                'reference': payment.reference_code,
                'batch_reference': payment.batch.reference_code if payment.batch else None,
            })
        
        return Response({
            'payments': payments_data,
            'total': len(payments_data),
            'total_amount': sum(p['amount'] for p in payments_data),
        })

