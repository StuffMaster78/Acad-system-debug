from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.db import models
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from writer_management.models.profile import WriterProfile
from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from writer_management.models.requests import WriterOrderRequest
from writer_management.models.payout import WriterPayment, WriterEarningsHistory
from writer_management.models.badges import WriterBadge, Badge
from orders.models import Order, WriterRequest
from order_payments_management.models import OrderPayment
from reviews_system.models.writer_review import WriterReview
from communications.models import CommunicationThread, CommunicationMessage


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
    
    def _is_within_days(self, date_string, days):
        """Helper to check if a date string is within N days."""
        if not date_string:
            return False
        try:
            from datetime import datetime
            msg_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            if isinstance(msg_date, datetime):
                msg_date = timezone.make_aware(msg_date) if timezone.is_naive(msg_date) else msg_date
            return (timezone.now() - msg_date).days <= days
        except Exception:
            return False

    def _get_order_pages(self, order):
        """Safe helper to read the number of pages on an order."""
        return (
            getattr(order, 'number_of_pages', None)
            or getattr(order, 'pages', None)
            or 0
        )

    def _get_completed_timestamp(self, order):
        """Return the best available completion/submission timestamp for an order."""
        completed_at = getattr(order, 'submitted_at', None)
        if completed_at:
            return completed_at
        return getattr(order, 'updated_at', None) or getattr(order, 'created_at', None)

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
        # Note: OrderPayment uses 'payments' as related_name, and status field is 'payment_status' or 'status'
        orders_with_payments = Order.objects.filter(
            assigned_writer=request.user,
            payments__status='completed'
        ).annotate(
            writer_payment=Sum('payments__amount', filter=Q(payments__status='completed'))
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
                    'status': getattr(p, 'status', 'Paid'),  # WriterPayment from payout doesn't have status
                    'created_at': p.payment_date.isoformat() if p.payment_date else None,
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
            writer=request.user,
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
        try:
            from writer_management.models.configs import WriterConfig
            
            profile = self.get_writer_profile(request)
            if not profile:
                return Response(
                    {"detail": "Writer profile not found."},
                    status=404
                )
            
            # Get writer config to check if takes are enabled
            try:
                writer_config = WriterConfig.objects.get(website=profile.website)
                takes_enabled = writer_config.takes_enabled
            except WriterConfig.DoesNotExist:
                takes_enabled = False
            
            # Get available orders (orders that can be taken)
            # Only show PAID orders that are available AND not already assigned
            # Exclude orders where this writer has declined
            from orders.models import PreferredWriterResponse
            
            declined_order_ids = list(PreferredWriterResponse.objects.filter(
                writer=profile.user,
                response='declined'
            ).values_list('order_id', flat=True))
            
            # Available orders: paid orders in common pool (not preferred for anyone, or preferred for this writer)
            available_orders = Order.objects.filter(
                status='available',
                website=profile.website,
                assigned_writer__isnull=True,  # Only unassigned orders
                is_paid=True,  # Only paid orders
            ).filter(
                # Either in common pool (preferred_writer is None) or preferred for this writer
                models.Q(preferred_writer__isnull=True) | models.Q(preferred_writer=request.user)
            )
            
            # Only exclude declined orders if there are any
            if declined_order_ids:
                available_orders = available_orders.exclude(id__in=declined_order_ids)
            
            available_orders = available_orders.select_related('client', 'type_of_work', 'paper_type').order_by('-created_at')[:50]
            
            # Get writer's order requests
            order_requests = WriterOrderRequest.objects.filter(
                writer=profile
            ).select_related('order').order_by('-requested_at')
            
            # Get list of order IDs that this writer has already requested
            requested_order_ids = list(order_requests.values_list('order_id', flat=True))
            
            # Get writer requests (from orders app)
            writer_requests = WriterRequest.objects.filter(
                requested_by_writer=request.user
            ).select_related('order').order_by('-created_at')
            
            # Add writer request order IDs to requested list
            writer_requested_order_ids = list(writer_requests.values_list('order_id', flat=True))
            requested_order_ids.extend(writer_requested_order_ids)
            
            # Get preferred orders (if client has preferred writers)
            # Only show PAID orders that are available and not assigned
            # Exclude orders where this writer has declined
            preferred_orders = Order.objects.filter(
                status='available',
                website=profile.website,
                assigned_writer__isnull=True,  # Only unassigned orders
                is_paid=True,  # Only paid orders
                preferred_writer=request.user  # Preferred for this writer
            )
            
            # Only exclude declined orders if there are any
            if declined_order_ids:
                preferred_orders = preferred_orders.exclude(id__in=declined_order_ids)
            
            preferred_orders = preferred_orders.select_related('client', 'type_of_work', 'paper_type').order_by('-created_at')[:20]
            
            return Response({
            'takes_enabled': takes_enabled,
            'requested_order_ids': requested_order_ids,  # Include requested order IDs for frontend
            'available_orders': [
                {
                    'id': o.id,
                    'topic': o.topic,
                    'is_requested': o.id in requested_order_ids,  # Flag if already requested
                    'service_type': getattr(o.type_of_work, 'name', str(o.type_of_work)) if o.type_of_work else 'Unknown',
                    'paper_type': getattr(o.paper_type, 'name', str(o.paper_type)) if o.paper_type else None,
                    'deadline': (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)).isoformat() if (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)) else None,
                    'pages': self._get_order_pages(o),
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
                    'status': getattr(r, 'status', 'pending'),
                    'created_at': r.requested_at.isoformat() if r.requested_at else None,
                    'requested_at': r.requested_at.isoformat() if r.requested_at else None,
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
                    'service_type': getattr(o.type_of_work, 'name', str(o.type_of_work)) if o.type_of_work else 'Unknown',
                    'paper_type': getattr(o.paper_type, 'name', str(o.paper_type)) if o.paper_type else None,
                    'deadline': (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)).isoformat() if (o.client_deadline or o.writer_deadline or getattr(o, 'deadline', None)) else None,
                    'pages': self._get_order_pages(o),
                    'price': float(o.total_price) if o.total_price else 0,
                    'created_at': o.created_at.isoformat() if o.created_at else None,
                    'is_requested': o.id in requested_order_ids,  # Flag if already requested
                }
                for o in preferred_orders
            ],
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_order_queue: {str(e)}", exc_info=True)
            return Response(
                {
                    "detail": "An error occurred while fetching order queue.",
                    "error": str(e)
                },
                status=500
            )
    
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
    
    @action(detail=False, methods=['get'], url_path='payments')
    def get_payments(self, request):
        """Get writer payments grouped by period (fortnightly/monthly) and upcoming payments."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        from django.db.models.functions import TruncMonth, TruncWeek
        from calendar import monthrange
        
        # Get historical payments from WriterPayment first
        historical_payments = WriterPayment.objects.filter(
            writer=profile
        ).order_by('-payment_date')
        
        # Get all completed paid orders
        completed_paid_orders = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            is_paid=True
        ).select_related('client', 'website').order_by('-submitted_at', '-created_at', '-updated_at')
        
        # Get completed orders that are paid but writer payment hasn't been processed yet (upcoming payments)
        # These are orders where client has paid, but WriterPayment record doesn't exist yet
        completed_paid_order_ids = list(completed_paid_orders.values_list('id', flat=True))
        
        # Note: WriterPayment model doesn't have an 'order' field, so we can't directly link payments to orders
        # Instead, we'll check if there's a payment record in writer_payments_management.WriterPayment
        # which does have an order field
        from writer_payments_management.models import WriterPayment as WriterPaymentWithOrder
        processed_order_ids = list(WriterPaymentWithOrder.objects.filter(
            writer=profile
        ).values_list('order_id', flat=True))
        
        # Upcoming payments: completed paid orders that don't have a WriterPayment record yet
        upcoming_order_ids = [oid for oid in completed_paid_order_ids if oid not in processed_order_ids]
        upcoming_orders = Order.objects.filter(
            id__in=upcoming_order_ids
        ).select_related('client', 'website').order_by('-submitted_at', '-created_at', '-updated_at') if upcoming_order_ids else Order.objects.none()
        
        # Group historical payments by month
        monthly_payments = historical_payments.annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(
            total_amount=Sum('amount'),
            total_bonuses=Sum('bonuses'),
            total_tips=Sum('tips'),
            total_fines=Sum('fines'),
            payment_count=Count('id')
        ).order_by('-month')
        
        # Group historical payments by fortnight (2-week periods)
        # Fortnight periods: 1-14 and 15-end of month
        fortnightly_payments = []
        payments_by_date = {}
        for payment in historical_payments:
            payment_date = payment.payment_date.date() if payment.payment_date else None
            if not payment_date:
                continue
            
            # Calculate fortnight start (1st-14th or 15th-end of month)
            if payment_date.day <= 14:
                fortnight_start = payment_date.replace(day=1)
                # End is 14th of same month
                try:
                    fortnight_end = payment_date.replace(day=14)
                except ValueError:
                    fortnight_end = payment_date.replace(day=13)  # Fallback for months with < 14 days
            else:
                fortnight_start = payment_date.replace(day=15)
                # End is last day of month
                last_day = monthrange(payment_date.year, payment_date.month)[1]
                fortnight_end = payment_date.replace(day=last_day)
            
            key = f"{fortnight_start.year}-{fortnight_start.month:02d}-{fortnight_start.day:02d}"
            if key not in payments_by_date:
                payments_by_date[key] = {
                    'period_start': fortnight_start.isoformat(),
                    'period_end': fortnight_end.isoformat(),
                    'total_amount': Decimal('0.00'),
                    'total_bonuses': Decimal('0.00'),
                    'total_tips': Decimal('0.00'),
                    'total_fines': Decimal('0.00'),
                    'payment_count': 0
                }
            
            payments_by_date[key]['total_amount'] += payment.amount or Decimal('0.00')
            payments_by_date[key]['total_bonuses'] += payment.bonuses or Decimal('0.00')
            payments_by_date[key]['total_tips'] += payment.tips or Decimal('0.00')
            payments_by_date[key]['total_fines'] += payment.fines or Decimal('0.00')
            payments_by_date[key]['payment_count'] += 1
        
        # Convert Decimal to float for JSON serialization
        fortnightly_payments = sorted(
            [
                {
                    'period_start': item['period_start'],
                    'period_end': item['period_end'],
                    'total_amount': float(item['total_amount']),
                    'total_bonuses': float(item['total_bonuses']),
                    'total_tips': float(item['total_tips']),
                    'total_fines': float(item['total_fines']),
                    'payment_count': item['payment_count'],
                }
                for item in payments_by_date.values()
            ],
            key=lambda x: x['period_start'],
            reverse=True
        )
        
        # Calculate upcoming payment totals
        # For upcoming payments, we need to calculate writer's expected earnings
        # This would typically be based on writer level pay rates, but for now use order price as estimate
        upcoming_total = sum(float(o.total_price or 0) for o in upcoming_orders)
        
        return Response({
            'historical_payments': {
                'monthly': [
                    {
                        'period': item['month'].isoformat() if item['month'] else None,
                        'total_amount': float(item['total_amount'] or 0),
                        'total_bonuses': float(item['total_bonuses'] or 0),
                        'total_tips': float(item['total_tips'] or 0),
                        'total_fines': float(item['total_fines'] or 0),
                        'payment_count': item['payment_count'],
                    }
                    for item in monthly_payments
                ],
                'fortnightly': fortnightly_payments,
            },
            'upcoming_payments': {
                'total_amount': upcoming_total,
                'order_count': upcoming_orders.count(),
                'orders': [
                    {
                        'id': o.id,
                        'topic': o.topic,
                        'total_price': float(o.total_price or 0),
                        'completed_at': (
                            completed_ts.isoformat() if (completed_ts := self._get_completed_timestamp(o)) else None
                        ),
                        'created_at': o.created_at.isoformat() if o.created_at else None,
                        'status': o.status,
                    }
                    for o in upcoming_orders[:50]
                ],
            },
            'recent_payments': [
                {
                    'id': p.id,
                    'amount': float(p.amount),
                    'bonuses': float(p.bonuses or 0),
                    'tips': float(p.tips or 0),
                    'fines': float(p.fines or 0),
                    'payment_date': p.payment_date.isoformat() if p.payment_date else None,
                    'description': p.description or '',
                    'currency': p.currency,
                }
                for p in historical_payments[:20]
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='level')
    def get_level(self, request):
        """Get writer level, earnings info, and progression requirements."""
        try:
            from writer_management.services.level_progression import WriterLevelProgressionService
            from writer_management.models.levels import WriterLevel
            
            profile = self.get_writer_profile(request)
            if not profile:
                return Response(
                    {"detail": "Writer profile not found."},
                    status=404
                )
            
            # Get current level
            current_level = profile.writer_level
            level_name = current_level.name if current_level else 'None'
            
            # Get level details if exists
            level_info = None
            if current_level:
                level_info = {
                    'id': current_level.id,
                    'name': current_level.name,
                    'description': current_level.description or '',
                    'earning_mode': current_level.earning_mode,
                    'base_pay_per_page': float(current_level.base_pay_per_page),
                    'base_pay_per_slide': float(current_level.base_pay_per_slide),
                    'earnings_percentage_of_cost': float(current_level.earnings_percentage_of_cost) if current_level.earnings_percentage_of_cost else None,
                    'earnings_percentage_of_total': float(current_level.earnings_percentage_of_total) if current_level.earnings_percentage_of_total else None,
                    'urgency_percentage_increase': float(current_level.urgency_percentage_increase),
                    'urgency_additional_per_page': float(current_level.urgency_additional_per_page),
                    'urgent_order_deadline_hours': current_level.urgent_order_deadline_hours,
                    'deadline_percentage': float(current_level.deadline_percentage),
                    'tips_percentage': float(current_level.tips_percentage),
                    'max_orders': current_level.max_orders,
                    'bonus_per_order_completed': float(current_level.bonus_per_order_completed),
                    'bonus_per_rating_above_threshold': float(current_level.bonus_per_rating_above_threshold),
                    'rating_threshold_for_bonus': float(current_level.rating_threshold_for_bonus),
                    'technical_order_adjustment_per_page': float(current_level.technical_order_adjustment_per_page),
                    'technical_order_adjustment_per_slide': float(current_level.technical_order_adjustment_per_slide),
                }
            
            # Get next level requirements
            next_level_info = WriterLevelProgressionService.get_next_level_requirements(profile)
            
            # Get current stats for progression
            stats = WriterLevelProgressionService._get_writer_stats(profile)
            
            # Get performance snapshot for ranking
            latest_snapshot = None
            ranking_position = None
            try:
                latest_snapshot = WriterPerformanceSnapshot.objects.filter(
                    writer=profile
                ).order_by('-generated_at').first()
                
                if latest_snapshot:
                    better_writers = WriterPerformanceSnapshot.objects.filter(
                        website=profile.website,
                        generated_at=latest_snapshot.generated_at,
                        average_rating__gt=latest_snapshot.average_rating
                    ).count()
                    ranking_position = better_writers + 1
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"WriterPerformanceSnapshot table not available: {e}")
            
            return Response({
                'current_level': level_info,
                'current_stats': {
                    'total_completed_orders': stats['total_completed_orders'],
                    'total_takes': stats['total_takes'],
                    'avg_rating': stats['avg_rating'],
                    'completion_rate': stats['completion_rate'],
                    'revision_rate': stats['revision_rate'],
                    'lateness_rate': stats['lateness_rate'],
                },
                'next_level': next_level_info,
                'ranking_position': ranking_position,
                'latest_snapshot': {
                    'average_rating': float(latest_snapshot.average_rating) if latest_snapshot else None,
                    'total_orders': latest_snapshot.total_orders if latest_snapshot else 0,
                    'completion_rate': float(latest_snapshot.completion_rate) if latest_snapshot and hasattr(latest_snapshot, 'completion_rate') else None,
                } if latest_snapshot else None,
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_level: {str(e)}", exc_info=True)
            return Response(
                {
                    "detail": "An error occurred while fetching level information.",
                    "error": str(e)
                },
                status=500
            )
    
    @action(detail=False, methods=['get'], url_path='estimated-earnings')
    def get_estimated_earnings(self, request):
        """Get estimated earnings for an order based on writer's level."""
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        from decimal import Decimal
        
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        if not profile.writer_level:
            return Response({
                "detail": "Writer level not assigned.",
                "estimated_earnings": 0.0,
            })
        
        # Get parameters from query string
        pages = int(request.query_params.get('pages', 10))
        slides = int(request.query_params.get('slides', 0))
        order_total = request.query_params.get('order_total')
        order_cost = request.query_params.get('order_cost')
        is_urgent = request.query_params.get('is_urgent', 'false').lower() == 'true'
        is_technical = request.query_params.get('is_technical', 'false').lower() == 'true'
        
        # Convert to Decimal if provided
        order_total_decimal = Decimal(str(order_total)) if order_total else None
        order_cost_decimal = Decimal(str(order_cost)) if order_cost else None
        
        # Calculate estimated earnings
        breakdown = WriterEarningsCalculator.calculate_estimated_earnings(
            profile.writer_level,
            pages=pages,
            slides=slides,
            order_total=order_total_decimal,
            order_cost=order_cost_decimal,
            is_urgent=is_urgent,
            is_technical=is_technical
        )
        
        return Response({
            'estimated_earnings': breakdown,
            'level_info': {
                'name': profile.writer_level.name,
                'earning_mode': profile.writer_level.earning_mode,
            }
        })
    
    @action(detail=False, methods=['get'], url_path='calendar')
    def get_calendar(self, request):
        """Get writer's order deadlines in calendar format."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get date range (default to current month, can be extended)
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if from_date:
            from_date = timezone.datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        else:
            from_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if to_date:
            to_date = timezone.datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        else:
            # Default to end of current month
            next_month = from_date.replace(day=28) + timedelta(days=4)
            to_date = next_month - timedelta(days=next_month.day)
            to_date = to_date.replace(hour=23, minute=59, second=59)
        
        # Get assigned orders with deadlines
        assigned_orders = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['in_progress', 'on_hold', 'revision_requested'],
        ).select_related('client', 'type_of_work', 'paper_type')
        
        # Build calendar data
        calendar_data = {}
        for order in assigned_orders:
            # Use writer_deadline, client_deadline, or deadline (in that order)
            deadline = order.writer_deadline or order.client_deadline or getattr(order, 'deadline', None)
            if not deadline:
                continue
            
            # Only include if within date range
            if deadline < from_date or deadline > to_date:
                continue
            
            date_key = deadline.date().isoformat()
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            
            # Calculate time remaining
            now = timezone.now()
            time_remaining = deadline - now
            hours_remaining = time_remaining.total_seconds() / 3600
            is_overdue = deadline < now
            is_urgent = hours_remaining <= 24 and hours_remaining > 0
            
            calendar_data[date_key].append({
                'id': order.id,
                'topic': order.topic or 'No topic',
                'service_type': getattr(order.type_of_work, 'name', str(order.type_of_work)) if order.type_of_work else 'Unknown',
                'pages': self._get_order_pages(order),
                'deadline': deadline.isoformat(),
                'status': order.status,
                'is_overdue': is_overdue,
                'is_urgent': is_urgent,
                'hours_remaining': round(hours_remaining, 1) if not is_overdue else None,
                'total_price': float(order.total_price) if order.total_price else 0,
            })
        
        # Sort orders within each day by deadline
        for date_key in calendar_data:
            calendar_data[date_key].sort(key=lambda x: x['deadline'])
        
        return Response({
            'from_date': from_date.isoformat(),
            'to_date': to_date.isoformat(),
            'calendar': calendar_data,
            'total_orders': sum(len(orders) for orders in calendar_data.values()),
            'overdue_count': sum(
                1 for orders in calendar_data.values()
                for order in orders
                if order['is_overdue']
            ),
            'urgent_count': sum(
                1 for orders in calendar_data.values()
                for order in orders
                if order['is_urgent']
            ),
        })
    
    @action(detail=False, methods=['get'], url_path='calendar/export')
    def export_calendar_ics(self, request):
        """Export writer's order deadlines as ICS (iCalendar) file."""
        from django.http import HttpResponse
        from datetime import timedelta
        
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get date range (default to next 3 months)
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        if from_date:
            from_date = timezone.datetime.fromisoformat(from_date.replace('Z', '+00:00'))
        else:
            from_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if to_date:
            to_date = timezone.datetime.fromisoformat(to_date.replace('Z', '+00:00'))
        else:
            # Default to 3 months from now
            to_date = from_date + timedelta(days=90)
            to_date = to_date.replace(hour=23, minute=59, second=59)
        
        # Get assigned orders with deadlines
        assigned_orders = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['in_progress', 'on_hold', 'revision_requested'],
        ).select_related('client', 'type_of_work', 'paper_type', 'website')
        
        # Generate ICS content
        ics_lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Writing System//Writer Calendar//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
        ]
        
        now = timezone.now()
        for order in assigned_orders:
            # Use writer_deadline, client_deadline, or deadline (in that order)
            deadline = order.writer_deadline or order.client_deadline or getattr(order, 'deadline', None)
            if not deadline:
                continue
            
            # Only include if within date range
            if deadline < from_date or deadline > to_date:
                continue
            
            # Format dates for ICS (YYYYMMDDTHHMMSSZ)
            dtstart = deadline.strftime('%Y%m%dT%H%M%S')
            dtstamp = now.strftime('%Y%m%dT%H%M%S')
            
            # Create event
            summary = f"Order #{order.id}: {order.topic or 'No topic'}"
            description_parts = [
                f"Order ID: {order.id}",
                f"Topic: {order.topic or 'N/A'}",
                f"Service: {getattr(order.type_of_work, 'name', 'Unknown') if order.type_of_work else 'Unknown'}",
                f"Pages: {self._get_order_pages(order)}",
                f"Status: {order.status}",
            ]
            
            if order.total_price:
                description_parts.append(f"Price: ${order.total_price:,.2f}")
            
            if hasattr(order, 'website') and order.website:
                description_parts.append(f"Website: {order.website.name}")
            
            description = '\\n'.join(description_parts)
            
            # Calculate time remaining for urgency
            time_remaining = deadline - now
            hours_remaining = time_remaining.total_seconds() / 3600
            is_overdue = deadline < now
            is_urgent = hours_remaining <= 24 and hours_remaining > 0
            
            # Set alarm/reminder (1 day before for urgent, 3 days for normal)
            alarm_minutes = 1440 if is_urgent else 4320  # 1 day or 3 days before
            
            # Build event
            ics_lines.extend([
                'BEGIN:VEVENT',
                f'UID:order-{order.id}-{deadline.timestamp()}@writingsystem',
                f'DTSTART:{dtstart}',
                f'DTEND:{dtstart}',  # Single point in time event
                f'DTSTAMP:{dtstamp}',
                f'SUMMARY:{summary}',
                f'DESCRIPTION:{description}',
                f'STATUS:CONFIRMED',
                f'SEQUENCE:0',
                f'PRIORITY:{"1" if is_urgent or is_overdue else "5"}',
            ])
            
            # Add location if website exists
            if hasattr(order, 'website') and order.website:
                ics_lines.append(f'LOCATION:{order.website.name}')
            
            # Add URL to order
            website_domain = getattr(order.website, 'domain', '') if hasattr(order, 'website') and order.website else ''
            if website_domain:
                order_url = f"{website_domain}/orders/{order.id}"
                ics_lines.append(f'URL:{order_url}')
            
            # Add alarm/reminder
            ics_lines.extend([
                'BEGIN:VALARM',
                'TRIGGER:-PT{}M'.format(alarm_minutes),
                'ACTION:DISPLAY',
                f'DESCRIPTION:Reminder: {summary}',
                'END:VALARM',
            ])
            
            ics_lines.append('END:VEVENT')
        
        ics_lines.append('END:VCALENDAR')
        
        # Create HTTP response with ICS content
        response = HttpResponse('\r\n'.join(ics_lines), content_type='text/calendar; charset=utf-8')
        filename = f'writer_calendar_{now.strftime("%Y%m%d")}.ics'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @action(detail=False, methods=['get'], url_path='workload')
    def get_workload(self, request):
        """Get writer's current workload vs capacity."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get writer level to determine max orders
        writer_level = profile.writer_level
        max_orders = writer_level.max_orders if writer_level else 10  # Default to 10
        
        # Count current active orders
        active_orders = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['in_progress', 'on_hold', 'revision_requested', 'submitted', 'under_editing']
        )
        
        current_count = active_orders.count()
        capacity_percentage = (current_count / max_orders * 100) if max_orders > 0 else 0
        
        # Get orders by status breakdown
        status_breakdown = {}
        for status in ['in_progress', 'on_hold', 'revision_requested', 'submitted', 'under_editing']:
            status_breakdown[status] = active_orders.filter(status=status).count()
        
        # Calculate estimated completion time for current orders
        # (simplified - could be enhanced with actual completion time estimates)
        total_pages = sum(self._get_order_pages(o) for o in active_orders)
        
        # Estimate: assume average writing speed (e.g., 2 pages per hour)
        estimated_hours = total_pages / 2 if total_pages > 0 else 0
        
        # Get upcoming deadlines
        now = timezone.now()
        upcoming_deadlines = active_orders.filter(
            models.Q(writer_deadline__gte=now) |
            models.Q(client_deadline__gte=now) |
            models.Q(deadline__gte=now)
        ).order_by('writer_deadline', 'client_deadline', 'deadline')[:5]
        
        upcoming_deadlines_list = []
        for order in upcoming_deadlines:
            deadline = order.writer_deadline or order.client_deadline or getattr(order, 'deadline', None)
            if deadline:
                hours_remaining = (deadline - now).total_seconds() / 3600
                upcoming_deadlines_list.append({
                    'id': order.id,
                    'topic': order.topic or 'No topic',
                    'deadline': deadline.isoformat(),
                    'hours_remaining': round(hours_remaining, 1),
                    'pages': self._get_order_pages(order),
                })
        
        return Response({
            'capacity': {
                'current_orders': current_count,
                'max_orders': max_orders,
                'available_slots': max(0, max_orders - current_count),
                'capacity_percentage': round(capacity_percentage, 1),
                'is_at_capacity': current_count >= max_orders,
                'is_near_capacity': capacity_percentage >= 80,
            },
            'status_breakdown': status_breakdown,
            'workload_estimate': {
                'total_pages': total_pages,
                'estimated_hours': round(estimated_hours, 1),
                'estimated_days': round(estimated_hours / 8, 1),  # Assuming 8-hour workday
            },
            'upcoming_deadlines': upcoming_deadlines_list,
            'writer_level': {
                'name': writer_level.name if writer_level else 'None',
                'max_orders': max_orders,
            },
        })
    
    @action(detail=False, methods=['get'], url_path='order-requests')
    def get_order_requests(self, request):
        """Get writer's order request status with real-time tracking."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get all order requests for this writer
        order_requests = WriterOrderRequest.objects.filter(
            writer=profile
        ).select_related('order', 'order__client', 'reviewed_by', 'website').order_by('-requested_at')
        
        # Also get WriterRequest (from orders app)
        writer_requests = WriterRequest.objects.filter(
            requested_by_writer=request.user
        ).select_related('order').order_by('-created_at')
        
        # Combine and format requests
        requests_list = []
        
        # Process WriterOrderRequest
        for req in order_requests:
            order = req.order
            requests_list.append({
                'id': req.id,
                'type': 'order_request',
                'order_id': order.id,
                'order_topic': order.topic or 'No topic',
                'order_status': order.status,
                'order_price': float(order.total_price) if order.total_price else 0,
                'order_pages': self._get_order_pages(order),
                'requested_at': req.requested_at.isoformat() if req.requested_at else None,
                'status': 'approved' if req.approved else 'pending',
                'reviewed_by': req.reviewed_by.username if req.reviewed_by else None,
                'reviewed_at': None,  # Could add reviewed_at field if needed
            })
        
        # Process WriterRequest
        for req in writer_requests:
            order = req.order
            requests_list.append({
                'id': req.id,
                'type': 'writer_request',
                'order_id': order.id,
                'order_topic': order.topic or 'No topic',
                'order_status': order.status,
                'order_price': float(order.total_price) if order.total_price else 0,
                'order_pages': self._get_order_pages(order),
                'requested_at': req.created_at.isoformat() if req.created_at else None,
                'status': req.status if hasattr(req, 'status') else 'pending',
                'reviewed_by': None,
                'reviewed_at': None,
            })
        
        # Sort by requested_at (most recent first)
        requests_list.sort(key=lambda x: x['requested_at'] or '', reverse=True)
        
        # Calculate statistics
        total_requests = len(requests_list)
        pending_requests = len([r for r in requests_list if r['status'] == 'pending'])
        approved_requests = len([r for r in requests_list if r['status'] == 'approved' or r['status'] == 'accepted'])
        
        return Response({
            'requests': requests_list,
            'statistics': {
                'total': total_requests,
                'pending': pending_requests,
                'approved': approved_requests,
                'rejected': total_requests - pending_requests - approved_requests,
            },
            'last_updated': timezone.now().isoformat(),
        })
    
    @action(detail=False, methods=['get'], url_path='summary')
    def get_dashboard_summary(self, request):
        """Get comprehensive dashboard summary including revisions, tips, fines, reviews, and level progress."""
        try:
            profile = self.get_writer_profile(request)
            if not profile:
                return Response(
                    {"detail": "Writer profile not found."},
                    status=404
                )
            
            # Get revision requests (orders needing revision)
            revision_orders = Order.objects.filter(
                assigned_writer=request.user,
                status='revision_requested'
            ).select_related('client', 'type_of_work').order_by('-updated_at')[:10]
            
            revision_requests = [
                {
                    'id': o.id,
                    'topic': o.topic or 'No topic',
                    'client_name': o.client.username if o.client else 'N/A',
                    'pages': self._get_order_pages(o),
                    'updated_at': o.updated_at.isoformat() if o.updated_at else None,
                    'deadline': (o.writer_deadline or o.client_deadline or getattr(o, 'deadline', None)).isoformat() if (o.writer_deadline or o.client_deadline or getattr(o, 'deadline', None)) else None,
                    'total_price': float(o.total_price) if o.total_price else 0,
                }
                for o in revision_orders
            ]
            
            # Get tips summary
            tips_summary = WriterPayment.objects.filter(
                writer=profile
            ).aggregate(
                total_tips=Sum('tips'),
                tips_count=Count('id', filter=Q(tips__gt=0)),
                this_month_tips=Sum('tips', filter=Q(payment_date__month=timezone.now().month, payment_date__year=timezone.now().year)),
            )
            
            # Get fines summary
            fines_summary = WriterPayment.objects.filter(
                writer=profile
            ).aggregate(
                total_fines=Sum('fines'),
                fines_count=Count('id', filter=Q(fines__gt=0)),
                this_month_fines=Sum('fines', filter=Q(payment_date__month=timezone.now().month, payment_date__year=timezone.now().year)),
                unpaid_fines=Sum('fines', filter=Q(fines__gt=0)),  # Assuming fines are deducted from payments
            )
            
            # Get recent reviews
            # WriterReview has: writer, website, reviewer (not order or client)
            try:
                recent_reviews = WriterReview.objects.filter(
                    writer=request.user
                ).select_related('reviewer', 'writer', 'website').order_by('-submitted_at')[:5]
            except Exception:
                # Fallback if submitted_at doesn't exist
                recent_reviews = WriterReview.objects.filter(
                    writer=request.user
                ).select_related('reviewer', 'writer', 'website').order_by('-id')[:5]
            
            recent_reviews_list = []
            for r in recent_reviews:
                # Get created_at from various possible field names
                created_at = None
                if hasattr(r, 'created_at') and r.created_at:
                    created_at = r.created_at.isoformat()
                elif hasattr(r, 'submitted_at') and r.submitted_at:
                    created_at = r.submitted_at.isoformat()
                elif hasattr(r, 'date_created') and r.date_created:
                    created_at = r.date_created.isoformat()
                
                # WriterReview doesn't have order or client fields
                # It has: writer, website, reviewer (the reviewer is typically the client)
                recent_reviews_list.append({
                    'id': r.id,
                    'order_id': None,  # WriterReview doesn't have an order field
                    'rating': float(r.rating) if r.rating else None,
                    'comment': r.comment or '',
                    'client_name': r.reviewer.username if r.reviewer else 'N/A',  # Reviewer is the client
                    'created_at': created_at,
                    'order_topic': 'N/A',  # WriterReview doesn't have an order field
                })
            
            # Calculate average rating
            avg_rating = WriterReview.objects.filter(
                writer=request.user
            ).aggregate(avg=Avg('rating'))['avg']
            
            # Get level progress
            writer_level = profile.writer_level
            current_level_name = writer_level.name if writer_level else 'None'
            
            # Get next level requirements (simplified - would need WriterLevelConfig)
            from writer_management.models.configs import WriterLevelConfig
            from writer_management.models.metrics import WriterPerformanceMetrics
            
            next_level = None
            progress_to_next = None
            
            try:
                # Get current metrics
                metrics = WriterPerformanceMetrics.objects.filter(writer=profile).first()
                
                if metrics and writer_level:
                    # Find next level
                    level_configs = WriterLevelConfig.objects.filter(
                        website=profile.website,
                        is_active=True
                    ).order_by('-priority')
                    
                    current_config = None
                    next_config = None
                    
                    for config in level_configs:
                        if config.name == current_level_name:
                            current_config = config
                            # Next config is the one with higher priority (lower number or higher score requirement)
                            idx = list(level_configs).index(config)
                            if idx > 0:
                                next_config = list(level_configs)[idx - 1]
                            break
                    
                    if next_config and metrics:
                        # Calculate progress
                        current_score = float(metrics.composite_score or 0)
                        required_score = float(next_config.min_score or 0)
                        
                        if required_score > current_score:
                            progress = (current_score / required_score * 100) if required_score > 0 else 0
                            progress_to_next = {
                                'current_score': current_score,
                                'required_score': required_score,
                                'progress_percentage': round(progress, 1),
                                'next_level_name': next_config.name,
                                'points_needed': round(required_score - current_score, 2),
                            }
                        else:
                            progress_to_next = {
                                'current_score': current_score,
                                'required_score': required_score,
                                'progress_percentage': 100,
                                'next_level_name': next_config.name,
                                'points_needed': 0,
                                'ready_for_promotion': True,
                            }
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error calculating level progress: {e}")
                progress_to_next = None
            
            return Response({
                'revision_requests': {
                    'count': revision_orders.count(),
                    'orders': revision_requests,
                },
                'tips': {
                    'total': float(tips_summary['total_tips'] or 0),
                    'count': tips_summary['tips_count'] or 0,
                    'this_month': float(tips_summary['this_month_tips'] or 0),
                },
                'fines': {
                    'total': float(fines_summary['total_fines'] or 0),
                    'count': fines_summary['fines_count'] or 0,
                    'this_month': float(fines_summary['this_month_fines'] or 0),
                    'unpaid': float(fines_summary['unpaid_fines'] or 0),
                },
                'reviews': {
                    'recent': recent_reviews_list,
                    'average_rating': float(avg_rating) if avg_rating else None,
                    'total_count': WriterReview.objects.filter(writer=request.user).count(),
                },
                'level_progress': progress_to_next,
                'current_level': {
                    'name': current_level_name,
                    'id': writer_level.id if writer_level else None,
                },
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_dashboard_summary: {str(e)}", exc_info=True)
            return Response(
                {
                    "detail": "An error occurred while fetching dashboard summary.",
                    "error": str(e)
                },
                status=500
            )
    
    @action(detail=False, methods=['get'], url_path='communications')
    def get_communications(self, request):
        """Get writer's communication threads and unread messages summary."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get all threads where writer is involved (via assigned orders or as participant)
        writer_orders = Order.objects.filter(assigned_writer=request.user)
        
        # Get threads for writer's orders
        order_threads = CommunicationThread.objects.filter(
            order__in=writer_orders
        ).select_related('order', 'order__client').prefetch_related('participants', 'messages')
        
        # Get threads where writer is a participant
        participant_threads = CommunicationThread.objects.filter(
            participants=request.user
        ).select_related('order', 'order__client').prefetch_related('participants', 'messages')
        
        # Combine and get unique threads
        all_threads = (order_threads | participant_threads).distinct()
        
        # Get unread message count per thread
        threads_summary = []
        total_unread = 0
        
        for thread in all_threads:
            # Count unread messages for this writer
            unread_count = CommunicationMessage.objects.filter(
                thread=thread,
                recipient=request.user,
                is_read=False,
                is_hidden=False
            ).count()
            
            total_unread += unread_count
            
            # Get last message
            last_message = CommunicationMessage.objects.filter(
                thread=thread,
                is_hidden=False
            ).order_by('-created_at').first()
            
            # Get other participants (excluding current writer)
            other_participants = thread.participants.exclude(id=request.user.id)
            client = thread.order.client if thread.order else None
            
            threads_summary.append({
                'id': thread.id,
                'order_id': thread.order.id if thread.order else None,
                'order_topic': thread.order.topic if thread.order else 'No topic',
                'order_status': thread.order.status if thread.order else None,
                'client_name': client.username if client else 'N/A',
                'client_id': client.id if client else None,
                'thread_type': thread.thread_type,
                'is_active': thread.is_active,
                'unread_count': unread_count,
                'last_message': {
                    'id': last_message.id if last_message else None,
                    'sender': last_message.sender.username if last_message else None,
                    'sender_role': last_message.sender_role if last_message else None,
                    'message': last_message.message[:100] + '...' if last_message and len(last_message.message) > 100 else (last_message.message if last_message else ''),
                    'created_at': last_message.created_at.isoformat() if last_message and hasattr(last_message, 'created_at') and last_message.created_at else None,
                    'has_attachment': bool(last_message.attachment) if last_message else False,
                } if last_message else None,
                'participants_count': thread.participants.count(),
                'created_at': thread.created_at.isoformat() if hasattr(thread, 'created_at') and thread.created_at else None,
                'updated_at': thread.updated_at.isoformat() if hasattr(thread, 'updated_at') and thread.updated_at else None,
            })
        
        # Sort by last message time (most recent first)
        threads_summary.sort(
            key=lambda x: x['last_message']['created_at'] if x['last_message'] and x['last_message']['created_at'] else '',
            reverse=True
        )
        
        # Get threads by client
        threads_by_client = {}
        for thread_data in threads_summary:
            client_id = thread_data['client_id']
            if client_id:
                if client_id not in threads_by_client:
                    threads_by_client[client_id] = {
                        'client_id': client_id,
                        'client_name': thread_data['client_name'],
                        'threads': [],
                        'unread_count': 0,
                    }
                threads_by_client[client_id]['threads'].append(thread_data)
                threads_by_client[client_id]['unread_count'] += thread_data['unread_count']
        
        # Get active conversations (threads with unread messages or recent activity)
        from datetime import datetime
        active_threads = []
        for t in threads_summary:
            is_active = False
            if t['unread_count'] > 0:
                is_active = True
            elif t['last_message'] and t['last_message']['created_at']:
                try:
                    # Parse ISO format date
                    msg_date = datetime.fromisoformat(t['last_message']['created_at'].replace('Z', '+00:00'))
                    if isinstance(msg_date, datetime):
                        msg_date = timezone.make_aware(msg_date) if timezone.is_naive(msg_date) else msg_date
                    days_ago = (timezone.now() - msg_date).days
                    if days_ago < 7:
                        is_active = True
                except Exception:
                    pass
            if is_active:
                active_threads.append(t)
        
        return Response({
            'total_threads': len(threads_summary),
            'total_unread': total_unread,
            'active_conversations': len(active_threads),
            'threads': threads_summary[:50],  # Limit to 50 most recent
            'threads_by_client': list(threads_by_client.values()),
            'active_threads': active_threads[:20],  # Top 20 active
            'summary': {
                'threads_with_unread': len([t for t in threads_summary if t['unread_count'] > 0]),
                'threads_this_week': len([
                    t for t in threads_summary 
                    if t['last_message'] and t['last_message']['created_at'] and
                    self._is_within_days(t['last_message']['created_at'], 7)
                ]),
            },
        })

