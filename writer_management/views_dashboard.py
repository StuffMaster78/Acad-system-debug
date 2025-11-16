from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from writer_management.models.profile import WriterProfile
from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from writer_management.models.requests import WriterOrderRequest
from writer_management.models.payout import WriterPayment, WriterEarningsHistory
from orders.models import Order, WriterRequest
from order_payments_management.models import OrderPayment
from reviews_system.models.writer_review import WriterReview


class WriterDashboardViewSet(viewsets.ViewSet):
    """API for writer dashboard statistics and analytics."""
    permission_classes = [IsAuthenticated]

    def get_writer_profile(self, request):
        """Get the writer profile for the current user."""
        if request.user.role != 'writer':
            return None
        try:
            return request.user.writer_profile
        except WriterProfile.DoesNotExist:
            return None

    @action(detail=False, methods=['get'], url_path='earnings')
    def get_earnings(self, request):
        """Get earnings breakdown and trends."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get writer's payments
        payments = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=date_from
        )
        
        # Earnings breakdown
        total_earnings = payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        # Note: WriterPayment doesn't have a status field, so all payments are considered completed
        pending_payments = Decimal('0.00')
        
        # Earnings by period
        week_start = timezone.now() - timedelta(days=7)
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        week_earnings = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=week_start
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        month_earnings = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=month_start
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        year_earnings = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=year_start
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Earnings trends (daily)
        earnings_trend = payments.annotate(
            date=TruncDate('payment_date')
        ).values('date').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('date')
        
        # Earnings by order type
        orders_with_payments = Order.objects.filter(
            assigned_writer=request.user,
            orderpayment__status='completed'
        ).annotate(
            writer_payment=Sum('orderpayment__amount', filter=Q(orderpayment__status='completed'))
        )
        
        # Average earnings per order
        avg_earnings_per_order = payments.aggregate(Avg('amount'))['amount__avg'] or Decimal('0.00')
        
        # Payment history
        payment_history = WriterPayment.objects.filter(
            writer=profile
        ).order_by('-payment_date')[:20]
        
        return Response({
            'total_earnings': float(total_earnings),
            'pending_payments': float(pending_payments),
            'this_week': float(week_earnings),
            'this_month': float(month_earnings),
            'this_year': float(year_earnings),
            'avg_per_order': float(avg_earnings_per_order),
            'earnings_trend': [
                {
                    'date': item['date'].isoformat() if item['date'] else None,
                    'total': float(item['total'] or 0),
                    'count': item['count'],
                }
                for item in earnings_trend
            ],
            'payment_history': [
                {
                    'id': p.id,
                    'amount': float(p.amount),
                    'status': p.status,
                    'created_at': p.created_at.isoformat() if p.created_at else None,
                    'description': p.description or '',
                }
                for p in payment_history
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='performance')
    def get_performance(self, request):
        """Get performance analytics."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get writer's orders
        orders = Order.objects.filter(
            assigned_writer=request.user,
            created_at__gte=date_from
        )
        
        # Performance metrics
        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        
        # Check for on-time/late orders (check if completed_at field exists)
        completed_orders_qs = orders.filter(status='completed')
        on_time_orders = 0
        late_orders = 0
        for order in completed_orders_qs:
            completed_at = getattr(order, 'completed_at', None)
            deadline = getattr(order, 'client_deadline', None) or getattr(order, 'writer_deadline', None) or getattr(order, 'deadline', None)
            if completed_at and deadline:
                if completed_at <= deadline:
                    on_time_orders += 1
                else:
                    late_orders += 1
        
        revised_orders = orders.filter(status='on_revision').count()
        
        # Calculate rates
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        on_time_rate = (on_time_orders / completed_orders * 100) if completed_orders > 0 else 0
        revision_rate = (revised_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Quality scores
        reviews = WriterReview.objects.filter(
            writer=profile,
            submitted_at__gte=date_from
        )
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Performance trends
        performance_trend = orders.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            completed=Count('id', filter=Q(status='completed')),
            total=Count('id')
        ).order_by('date')
        
        return Response({
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'on_time_orders': on_time_orders,
            'late_orders': late_orders,
            'revised_orders': revised_orders,
            'completion_rate': completion_rate,
            'on_time_rate': on_time_rate,
            'revision_rate': revision_rate,
            'avg_rating': float(avg_rating) if avg_rating else None,
            'performance_trend': [
                {
                    'date': item['date'].isoformat() if item['date'] else None,
                    'completed': item['completed'],
                    'total': item['total'],
                }
                for item in performance_trend
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='queue')
    def get_order_queue(self, request):
        """Get available orders and order requests."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get available orders (orders that can be taken)
        available_orders = Order.objects.filter(
            status='available',
            website=profile.website
        ).select_related('client', 'service_type').order_by('-created_at')[:50]
        
        # Get writer's order requests
        order_requests = WriterOrderRequest.objects.filter(
            writer=profile
        ).select_related('order').order_by('-created_at')
        
        # Get writer requests (from orders app)
        writer_requests = WriterRequest.objects.filter(
            writer=request.user
        ).select_related('order').order_by('-created_at')
        
        # Get preferred orders (if client has preferred writers)
        preferred_orders = Order.objects.filter(
            status='available',
            website=profile.website,
            client__client_profile__preferred_writers=request.user
        ).select_related('client', 'service_type').order_by('-created_at')[:20]
        
        return Response({
            'available_orders': [
                {
                    'id': o.id,
                    'topic': o.topic,
                    'service_type': getattr(o.service_type, 'name', str(o.service_type)) if o.service_type else 'Unknown',
                    'deadline': (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)).isoformat() if (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)) else None,
                    'pages': o.pages or 0,
                    'price': float(o.total_price) if o.total_price else 0,
                    'created_at': o.created_at.isoformat() if o.created_at else None,
                }
                for o in available_orders
            ],
            'order_requests': [
                {
                    'id': r.id,
                    'order_id': r.order.id if r.order else None,
                    'order_topic': r.order.topic if r.order else None,
                    'approved': r.approved,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                }
                for r in order_requests[:20]
            ],
            'writer_requests': [
                {
                    'id': r.id,
                    'order_id': r.order.id if r.order else None,
                    'order_topic': r.order.topic if r.order else None,
                    'status': r.status,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                }
                for r in writer_requests[:20]
            ],
            'preferred_orders': [
                {
                    'id': o.id,
                    'topic': o.topic,
                    'service_type': getattr(o.service_type, 'name', str(o.service_type)) if o.service_type else 'Unknown',
                    'deadline': (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)).isoformat() if (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)) else None,
                    'pages': o.pages or 0,
                    'price': float(o.total_price) if o.total_price else 0,
                    'created_at': o.created_at.isoformat() if o.created_at else None,
                }
                for o in preferred_orders
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='badges')
    def get_badges(self, request):
        """Get badges and achievements."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get writer's badges
        writer_badges = WriterBadge.objects.filter(
            writer=profile,
            revoked=False
        ).select_related('badge').order_by('-issued_at')
        
        # Get all available badges for reference
        # Note: Badge model uses 'Website' (capital W) as the field name
        all_badges = Badge.objects.filter(
            is_active=True,
            Website=profile.website
        ).order_by('type', 'name')
        
        # Get badge counts by type
        badge_counts = writer_badges.values('badge__type').annotate(
            count=Count('id')
        )
        badge_counts_dict = {item['badge__type']: item['count'] for item in badge_counts}
        
        # Get recent badges
        recent_badges = writer_badges[:10]
        
        # Get next milestones (simplified - would need proper milestone logic)
        milestones = []
        
        return Response({
            'badges': [
                {
                    'id': wb.id,
                    'badge_id': wb.badge.id,
                    'name': wb.badge.name,
                    'icon': wb.badge.icon,
                    'type': wb.badge.type,
                    'description': wb.badge.description,
                    'issued_at': wb.issued_at.isoformat() if wb.issued_at else None,
                    'is_auto_awarded': wb.is_auto_awarded,
                }
                for wb in writer_badges
            ],
            'recent_badges': [
                {
                    'id': wb.id,
                    'badge_id': wb.badge.id,
                    'name': wb.badge.name,
                    'icon': wb.badge.icon,
                    'type': wb.badge.type,
                    'issued_at': wb.issued_at.isoformat() if wb.issued_at else None,
                }
                for wb in recent_badges
            ],
            'badge_counts_by_type': badge_counts_dict,
            'total_badges': writer_badges.count(),
            'available_badges': [
                {
                    'id': b.id,
                    'name': b.name,
                    'icon': b.icon,
                    'type': b.type,
                    'description': b.description,
                    'auto_award': b.auto_award,
                }
                for b in all_badges
            ],
            'milestones': milestones,
        })
    
    @action(detail=False, methods=['get'], url_path='level')
    def get_level(self, request):
        """Get writer level and ranking information."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get current level
        current_level = profile.writer_level
        level_name = current_level.name if current_level else 'None'
        
        # Get performance snapshot for ranking
        # Handle case where table doesn't exist (migrations not run)
        latest_snapshot = None
        ranking_position = None
        try:
            latest_snapshot = WriterPerformanceSnapshot.objects.filter(
                writer=profile
            ).order_by('-generated_at').first()
            
            # Calculate ranking position (simplified - would need proper ranking logic)
            if latest_snapshot:
                # Count writers with better performance
                better_writers = WriterPerformanceSnapshot.objects.filter(
                    website=profile.website,
                    generated_at=latest_snapshot.generated_at,
                    average_rating__gt=latest_snapshot.average_rating
                ).count()
                ranking_position = better_writers + 1
        except Exception as e:
            # Table doesn't exist or other database error - gracefully handle
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"WriterPerformanceSnapshot table not available: {e}")
            latest_snapshot = None
            ranking_position = None
        
        return Response({
            'current_level': {
                'name': level_name,
                'id': current_level.id if current_level else None,
            },
            'ranking_position': ranking_position,
            'latest_snapshot': {
                'average_rating': float(latest_snapshot.average_rating) if latest_snapshot else None,
                'total_orders': latest_snapshot.total_orders if latest_snapshot else 0,
                'completion_rate': float(latest_snapshot.completion_rate) if latest_snapshot else None,
            } if latest_snapshot else None,
        })

