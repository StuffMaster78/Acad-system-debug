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

    @action(detail=False, methods=['get'], url_path='payment-info')
    def get_payment_info(self, request):
        """
        Get writer's payment information based on their level.
        Shows only level-based payment rates (per page, per slide, per class).
        Excludes installments and internal payment details.
        """
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        if not profile.writer_level:
            return Response(
                {"detail": "Writer level not set."},
                status=404
            )
        
        from writer_management.serializers import WriterPaymentViewSerializer
        
        # Get level-based rates
        level = profile.writer_level
        data = {
            'cost_per_page': level.base_pay_per_page,
            'cost_per_slide': level.base_pay_per_slide,
            'cost_per_class': getattr(level, 'base_pay_per_class', None),  # May not exist yet
            'level_name': level.name,
            'earning_mode': level.earning_mode,
        }
        
        # Calculate totals from orders, special orders
        serializer = WriterPaymentViewSerializer(profile, context={'request': request})
        serialized_data = serializer.data
        
        # Calculate totals
        order_earnings_list = serialized_data.get('order_earnings', [])
        special_order_earnings_list = serialized_data.get('special_order_earnings', [])
        class_bonuses_list = serialized_data.get('class_earnings', [])  # These are bonuses, not regular earnings
        
        total_order_earnings = sum(Decimal(str(e['amount'])) for e in order_earnings_list)
        total_special_order_earnings = sum(Decimal(str(e.get('total', e.get('amount', 0)))) for e in special_order_earnings_list)
        
        # Get bonuses and tips (excluding installments)
        from writer_management.models.payout import WriterPayment
        from special_orders.models import WriterBonus
        
        payments = WriterPayment.objects.filter(
            writer=profile
        ).exclude(
            # Exclude payments related to installments
            description__icontains='installment'
        )
        
        total_bonuses = payments.aggregate(Sum('bonuses'))['bonuses__sum'] or Decimal('0.00')
        total_tips = payments.aggregate(Sum('tips'))['tips__sum'] or Decimal('0.00')
        
        # Add class bonuses (classes are paid as bonuses, not regular earnings)
        class_bonuses_total = sum(Decimal(str(e.get('amount', 0))) for e in class_bonuses_list)
        total_bonuses += class_bonuses_total
        
        data.update({
            'order_earnings': order_earnings_list,
            'special_order_earnings': special_order_earnings_list,
            'class_bonuses': class_bonuses_list,  # Classes shown as bonuses but contribute to total earnings
            'total_earnings': total_order_earnings + total_special_order_earnings + class_bonuses_total,  # Classes contribute to total
            'total_bonuses': total_bonuses,  # Includes class bonuses
            'total_tips': total_tips,
        })
        
        return Response(data)
    
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
        
        # Get writer's payments (excluding installments)
        payments = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=date_from
        ).exclude(
            # Exclude payments related to installments
            description__icontains='installment'
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
        ).exclude(description__icontains='installment').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        month_earnings = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=month_start
        ).exclude(description__icontains='installment').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        year_earnings = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=year_start
        ).exclude(description__icontains='installment').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
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
            
            available_orders = list(
                available_orders.select_related('client', 'type_of_work', 'paper_type', 'subject').order_by('-created_at')[:50]
            )
            
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
            
            preferred_orders = list(
                preferred_orders.select_related('client', 'type_of_work', 'paper_type', 'subject').order_by('-created_at')[:20]
            )

            # ------------------------------------------------------------------
            # Intelligent recommendations & metadata
            # ------------------------------------------------------------------

            def _normalize_keywords(raw):
                if not raw:
                    return set()
                return {
                    segment.strip().lower()
                    for segment in raw.split(',')
                    if segment and segment.strip()
                }

            skill_keywords = _normalize_keywords(profile.skills or "")
            subject_keywords = _normalize_keywords(profile.subject_preferences or "")

            subject_pref_manager = getattr(profile, 'subject_preferences_for_specific_writer', None)
            if subject_pref_manager:
                for pref in subject_pref_manager.all():
                    for subject in pref.subjects or []:
                        if subject:
                            subject_keywords.add(subject.lower())

            keyword_bank = skill_keywords | subject_keywords
            high_payout_threshold = 150

            def _estimate_payout(order):
                compensation = getattr(order, 'writer_compensation', None) or Decimal('0.00')
                if compensation and compensation > 0:
                    return float(compensation)

                order_total = order.total_price or Decimal('0.00')
                level = getattr(profile, 'writer_level', None)
                if level:
                    try:
                        payout = level.calculate_order_payment(
                            pages=self._get_order_pages(order),
                            slides=getattr(order, 'number_of_slides', 0),
                            is_urgent=bool(getattr(order, 'is_urgent', False)),
                            is_technical=False,
                            order_total=order_total,
                            order_cost=order_total,
                        )
                        if payout:
                            return float(payout)
                    except Exception:
                        pass

                fallback_percentage = None
                if level:
                    fallback_percentage = (
                        level.earnings_percentage_of_total
                        or level.earnings_percentage_of_cost
                    )
                percentage = float(fallback_percentage or 55) / 100
                return float(order_total) * percentage if order_total else 0.0

            def _deadline_dt(order):
                return (
                    order.writer_deadline
                    or order.client_deadline
                    or getattr(order, 'deadline', None)
                    or order.created_at
                )

            def _compute_match_metadata(order):
                meta = {
                    'score': 0,
                    'tags': [],
                }
                subject_name = getattr(order.subject, 'name', None)
                type_of_work = getattr(order.type_of_work, 'name', None)
                topic_text = (order.topic or '').lower()

                if subject_name and subject_name.lower() in subject_keywords:
                    meta['score'] += 40
                    meta['tags'].append(f"Subject match: {subject_name}")

                if type_of_work and type_of_work.lower() in keyword_bank:
                    meta['score'] += 20
                    meta['tags'].append(f"Preferred work type: {type_of_work}")

                if topic_text and skill_keywords:
                    for skill in skill_keywords:
                        if skill and skill in topic_text:
                            meta['score'] += 10
                            meta['tags'].append(f"Topic mentions '{skill}'")
                            break

                potential_payout = round(_estimate_payout(order), 2)
                meta['potential_payout'] = potential_payout

                if potential_payout >= high_payout_threshold:
                    meta['score'] += 10
                    meta['tags'].append("High payout opportunity")

                meta['score'] = min(meta['score'], 100)
                meta['subject_name'] = subject_name
                meta['type_of_work'] = type_of_work
                meta['deadline'] = _deadline_dt(order)
                return meta

            candidate_orders = {}
            for order in available_orders + preferred_orders:
                candidate_orders[order.id] = order

            match_metadata = {
                order_id: _compute_match_metadata(order)
                for order_id, order in candidate_orders.items()
            }

            def _serialize_order(order):
                meta = match_metadata.get(order.id, {})
                deadline = (order.client_deadline or order.writer_deadline or getattr(order, 'deadline', None))
                return {
                    'id': order.id,
                    'topic': order.topic,
                    'subject': meta.get('subject_name'),
                    'service_type': getattr(order.type_of_work, 'name', str(order.type_of_work)) if order.type_of_work else 'Unknown',
                    'paper_type': getattr(order.paper_type, 'name', str(order.paper_type)) if order.paper_type else None,
                    'deadline': deadline.isoformat() if deadline else None,
                    'pages': self._get_order_pages(order),
                    'price': float(order.total_price) if order.total_price else 0,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'is_requested': order.id in requested_order_ids,
                    'match_score': meta.get('score', 0),
                    'match_tags': meta.get('tags', []),
                    'potential_payout': meta.get('potential_payout', 0),
                }

            recommended_candidates = [
                (order, match_metadata.get(order.id, {}))
                for order in candidate_orders.values()
                if order.id not in requested_order_ids
            ]

            recommended_candidates.sort(
                key=lambda item: (
                    -item[1].get('score', 0),
                    -item[1].get('potential_payout', 0),
                    item[1].get('deadline') or timezone.now(),
                )
            )

            recommended_orders = [
                _serialize_order(order)
                for order, _ in recommended_candidates[:10]
            ]
            
            # Get level capacity information
            writer_level = getattr(profile, 'writer_level', None)
            max_orders = writer_level.max_orders if writer_level else 0
            
            # Count active orders (in_progress, under_editing, revision_requested, on_hold)
            active_orders_count = Order.objects.filter(
                assigned_writer=profile.user,
                website=profile.website,
                status__in=['in_progress', 'under_editing', 'revision_requested', 'on_hold']
            ).count()
            
            remaining_slots = max(0, max_orders - active_orders_count)
            
            # Get level details
            level_details = None
            if writer_level:
                level_details = {
                    'id': writer_level.id,
                    'name': writer_level.name,
                    'max_orders': writer_level.max_orders,
                }
            
            return Response({
            'takes_enabled': takes_enabled,
            'requested_order_ids': requested_order_ids,  # Include requested order IDs for frontend
            'available_orders': [
                _serialize_order(o)
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
                _serialize_order(o)
                for o in preferred_orders
            ],
            'recommended_orders': recommended_orders,
            'level_capacity': {
                'level_details': level_details,
                'max_orders': max_orders,
                'active_orders': active_orders_count,
                'remaining_slots': remaining_slots,
            },
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

    @action(detail=False, methods=['get', 'post'], url_path='availability')
    def availability(self, request):
        """Get or update writer availability for instant assignments."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )

        if request.method.lower() == 'get':
            return Response(self._serialize_availability(profile))

        is_available = request.data.get('is_available')
        if is_available is None:
            return Response(
                {"detail": "'is_available' is required."},
                status=400
            )

        if isinstance(is_available, str):
            is_available = is_available.strip().lower() in ['1', 'true', 'yes', 'on']

        profile.is_available_for_auto_assignments = bool(is_available)
        profile.availability_message = (request.data.get('message') or '').strip()[:160]
        profile.availability_last_changed = timezone.now()
        profile.save(
            update_fields=[
                'is_available_for_auto_assignments',
                'availability_message',
                'availability_last_changed',
            ]
        )
        return Response(self._serialize_availability(profile))
    
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
        upcoming_orders = (
            Order.objects.filter(id__in=upcoming_order_ids)
            .select_related('client', 'website')
            .order_by('-submitted_at', '-created_at', '-updated_at')
            if upcoming_order_ids
            else Order.objects.none()
        )
        
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
        # Fortnight periods: 1-14 and 15-end of month (for historical display only)
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
        # For upcoming payments, we calculate writer's expected earnings based on writer level,
        # NOT the client total price (writers should never see client totals).
        from writer_management.services.earnings_calculator import WriterEarningsCalculator

        def _get_official_payment_window(completed_ts):
            """
            Determine the official payment window for a completed order based on:
            - Writer's payment_schedule (bi-weekly or monthly)
            - Business rules:
              * Orders completed 1st–15th → paid 17th–21st same month
              * Orders completed 16th–end of month → paid 5th–7th next month
            """
            if not completed_ts:
                return None

            from datetime import date

            completed_date = completed_ts.date()
            schedule = getattr(profile, 'payment_schedule', 'bi-weekly')

            if schedule == 'monthly':
                # Monthly: all orders in month N are scheduled 5–7 of month N+1
                year = completed_date.year
                month = completed_date.month + 1
                if month > 12:
                    month = 1
                    year += 1
                start = date(year, month, 5)
                end = date(year, month, 7)
            else:
                # Bi-weekly schedule with fixed official windows
                if completed_date.day <= 15:
                    # Window A: 1–15 → 17–21 same month
                    start = date(completed_date.year, completed_date.month, 17)
                    end = date(completed_date.year, completed_date.month, 21)
                else:
                    # Window B: 16–end → 5–7 of next month
                    year = completed_date.year
                    month = completed_date.month + 1
                    if month > 12:
                        month = 1
                        year += 1
                    start = date(year, month, 5)
                    end = date(year, month, 7)

            label = f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}"
            return {
                "start": start,
                "end": end,
                "label": label,
            }

        upcoming_orders_payload = []
        upcoming_total = Decimal('0.00')

        for o in upcoming_orders:
            completed_ts = self._get_completed_timestamp(o)

            # Determine urgency and technicality similar to WriterPayment.process_payment
            is_urgent = False
            writer_level = getattr(profile, 'writer_level', None)
            if getattr(o, 'writer_deadline', None) or getattr(o, 'client_deadline', None):
                deadline = getattr(o, 'writer_deadline', None) or getattr(o, 'client_deadline', None)
                if deadline and writer_level and getattr(writer_level, 'urgent_order_deadline_hours', None) is not None:
                    hours_until_deadline = (deadline - timezone.now()).total_seconds() / 3600
                    is_urgent = hours_until_deadline <= writer_level.urgent_order_deadline_hours

            is_technical = getattr(o, 'is_technical', False) or (
                hasattr(o, 'subject') and getattr(getattr(o, 'subject'), 'is_technical', False)
            )

            if writer_level:
                expected_earning = WriterEarningsCalculator.calculate_earnings(
                    writer_level,
                    o,
                    is_urgent=is_urgent,
                    is_technical=is_technical,
                )
            else:
                expected_earning = Decimal('0.00')

            window = _get_official_payment_window(completed_ts)

            upcoming_total += expected_earning

            upcoming_orders_payload.append(
                {
                    "id": o.id,
                    "topic": o.topic,
                    # Writer-facing: show only what the writer will earn for this order
                    "expected_earning": float(expected_earning),
                    "completed_at": completed_ts.isoformat() if completed_ts else None,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                    "status": o.status,
                    "expected_payment_window_start": window["start"].isoformat() if window else None,
                    "expected_payment_window_end": window["end"].isoformat() if window else None,
                    "expected_payment_window_label": window["label"] if window else None,
                }
            )
        
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
                'total_amount': float(upcoming_total),
                'order_count': len(upcoming_orders_payload),
                'orders': upcoming_orders_payload[:50],
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
    
    @action(detail=False, methods=['get'], url_path='payment-status')
    def get_payment_status(self, request):
        """Get comprehensive payment status dashboard for writer."""
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get payments from writer_payments_management
        from writer_payments_management.models import WriterPayment, WriterPayoutRequest
        
        all_payments = WriterPayment.objects.filter(
            writer=profile
        ).select_related('order', 'special_order', 'website')
        
        # Payment status breakdown
        status_breakdown = all_payments.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Pending payments
        pending_payments = all_payments.filter(status='Pending')
        pending_amount = pending_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Delayed payments
        delayed_payments = all_payments.filter(status='Delayed')
        delayed_amount = delayed_payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Paid payments (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        recent_paid = all_payments.filter(
            status='Paid',
            processed_at__gte=month_ago
        )
        recent_paid_amount = recent_paid.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Total earnings (all time)
        total_earnings = all_payments.filter(
            status='Paid'
        ).aggregate(
            total=Sum('amount'),
            total_bonuses=Sum('bonuses'),
            total_tips=Sum('tips'),
            total_fines=Sum('fines')
        )
        
        # Payment trends (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        payment_trends = all_payments.filter(
            processed_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('processed_at')
        ).values('week', 'status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('week', 'status')
        
        # Payout requests
        payout_requests = WriterPayoutRequest.objects.filter(
            writer=profile
        ).order_by('-requested_at')
        
        pending_payout_requests = payout_requests.filter(status='Pending')
        pending_payout_amount = pending_payout_requests.aggregate(
            total=Sum('amount_requested')
        )['total'] or Decimal('0.00')
        
        # Payment method status (payout preferences)
        payout_preferences = profile.payout_preferences.filter(verified=True)
        has_verified_payout_method = payout_preferences.exists()
        
        # Recent payment activity
        recent_payments = all_payments.order_by('-processed_at')[:10]
        
        # Payment schedule info (if available)
        # This would typically come from writer config or website settings
        payment_schedule = 'bi-weekly'  # Default, could be from config
        
        return Response({
            'summary': {
                'total_earnings': float(total_earnings['total'] or 0),
                'total_bonuses': float(total_earnings['total_bonuses'] or 0),
                'total_tips': float(total_earnings['total_tips'] or 0),
                'total_fines': float(total_earnings['total_fines'] or 0),
                'pending_amount': float(pending_amount),
                'delayed_amount': float(delayed_amount),
                'recent_paid_30d': float(recent_paid_amount),
                'pending_payout_requests': pending_payout_requests.count(),
                'pending_payout_amount': float(pending_payout_amount),
                'has_verified_payout_method': has_verified_payout_method,
                'payment_schedule': payment_schedule,
            },
            'status_breakdown': {
                item['status']: {
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0),
                }
                for item in status_breakdown
            },
            'pending_payments': [
                {
                    'id': p.id,
                    'order_id': p.order.id if p.order else None,
                    'special_order_id': p.special_order.id if p.special_order else None,
                    'amount': float(p.amount),
                    'bonuses': float(p.bonuses or 0),
                    'tips': float(p.tips or 0),
                    'fines': float(p.fines or 0),
                    'status': p.status,
                    'processed_at': p.processed_at.isoformat() if p.processed_at else None,
                }
                for p in pending_payments[:20]
            ],
            'delayed_payments': [
                {
                    'id': p.id,
                    'order_id': p.order.id if p.order else None,
                    'amount': float(p.amount),
                    'status': p.status,
                    'processed_at': p.processed_at.isoformat() if p.processed_at else None,
                    'updated_at': p.updated_at.isoformat() if p.updated_at else None,
                }
                for p in delayed_payments[:20]
            ],
            'payment_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'status': item['status'],
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0),
                }
                for item in payment_trends
            ],
            'payout_requests': [
                {
                    'id': req.id,
                    'amount_requested': float(req.amount_requested),
                    'status': req.status,
                    'requested_at': req.requested_at.isoformat() if req.requested_at else None,
                    'processed_at': req.processed_at.isoformat() if req.processed_at else None,
                }
                for req in payout_requests[:10]
            ],
            'recent_payments': [
                {
                    'id': p.id,
                    'order_id': p.order.id if p.order else None,
                    'amount': float(p.amount),
                    'bonuses': float(p.bonuses or 0),
                    'tips': float(p.tips or 0),
                    'fines': float(p.fines or 0),
                    'status': p.status,
                    'processed_at': p.processed_at.isoformat() if p.processed_at else None,
                }
                for p in recent_payments
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
    
    @action(detail=False, methods=['get'], url_path='workload-capacity')
    def get_workload_capacity(self, request):
        """Get comprehensive writer workload capacity indicator with recommendations."""
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
            status__in=['in_progress', 'on_hold', 'revision_requested', 'submitted', 'under_editing', 'on_revision']
        )
        
        current_count = active_orders.count()
        capacity_percentage = (current_count / max_orders * 100) if max_orders > 0 else 0
        
        # Get orders by status breakdown
        status_breakdown = {}
        for status in ['in_progress', 'on_hold', 'revision_requested', 'submitted', 'under_editing', 'on_revision']:
            status_breakdown[status] = active_orders.filter(status=status).count()
        
        # Calculate estimated completion time for current orders
        total_pages = sum(self._get_order_pages(o) for o in active_orders)
        
        # Estimate: assume average writing speed (e.g., 2 pages per hour)
        estimated_hours = total_pages / 2 if total_pages > 0 else 0
        
        # Get upcoming deadlines with urgency
        now = timezone.now()
        upcoming_deadlines = active_orders.filter(
            models.Q(writer_deadline__gte=now) |
            models.Q(client_deadline__gte=now)
        ).order_by('writer_deadline', 'client_deadline')[:10]
        
        upcoming_deadlines_list = []
        urgent_count = 0
        for order in upcoming_deadlines:
            deadline = order.writer_deadline or order.client_deadline
            if deadline:
                hours_remaining = (deadline - now).total_seconds() / 3600
                days_remaining = hours_remaining / 24
                is_urgent = hours_remaining < 24
                is_critical = hours_remaining < 12
                
                if is_urgent:
                    urgent_count += 1
                
                upcoming_deadlines_list.append({
                    'id': order.id,
                    'topic': order.topic or 'No topic',
                    'status': order.status,
                    'deadline': deadline.isoformat(),
                    'hours_remaining': round(hours_remaining, 1),
                    'days_remaining': round(days_remaining, 2),
                    'pages': self._get_order_pages(order),
                    'is_urgent': is_urgent,
                    'is_critical': is_critical,
                })
        
        # Availability status
        is_available = getattr(profile, 'is_available_for_auto_assignments', True)
        availability_status = 'available' if is_available else 'unavailable'
        if current_count >= max_orders:
            availability_status = 'at_capacity'
        elif capacity_percentage >= 90:
            availability_status = 'near_capacity'
        elif urgent_count > 0:
            availability_status = 'busy'
        
        # Workload recommendations
        recommendations = []
        if current_count >= max_orders:
            recommendations.append({
                'type': 'warning',
                'message': f'You are at maximum capacity ({current_count}/{max_orders} orders). Consider completing existing orders before taking new ones.',
                'priority': 'high',
            })
        elif capacity_percentage >= 90:
            recommendations.append({
                'type': 'info',
                'message': f'You are near capacity ({current_count}/{max_orders} orders). You have {max_orders - current_count} slot(s) remaining.',
                'priority': 'medium',
            })
        
        if urgent_count > 0:
            recommendations.append({
                'type': 'urgent',
                'message': f'You have {urgent_count} order(s) with deadlines within 24 hours. Focus on completing these first.',
                'priority': 'high',
            })
        
        if estimated_hours > 40:  # More than a week of work
            recommendations.append({
                'type': 'info',
                'message': f'Your current workload is estimated at {round(estimated_hours, 1)} hours. Plan your schedule accordingly.',
                'priority': 'medium',
            })
        
        if not is_available and current_count < max_orders:
            recommendations.append({
                'type': 'info',
                'message': 'You have marked yourself as unavailable for auto-assignments. You can still manually request orders.',
                'priority': 'low',
            })
        
        # Calculate average pages per order
        avg_pages_per_order = total_pages / current_count if current_count > 0 else 0
        
        # Estimate time to clear current workload
        estimated_days_to_clear = round(estimated_hours / 8, 1) if estimated_hours > 0 else 0  # Assuming 8-hour workday
        
        # Capacity health indicator
        if current_count >= max_orders:
            capacity_health = 'overloaded'
        elif capacity_percentage >= 90:
            capacity_health = 'high'
        elif capacity_percentage >= 70:
            capacity_health = 'moderate'
        elif capacity_percentage >= 50:
            capacity_health = 'comfortable'
        else:
            capacity_health = 'light'
        
        return Response({
            'capacity': {
                'current_orders': current_count,
                'max_orders': max_orders,
                'available_slots': max(0, max_orders - current_count),
                'capacity_percentage': round(capacity_percentage, 1),
                'capacity_health': capacity_health,
                'is_at_capacity': current_count >= max_orders,
                'is_near_capacity': capacity_percentage >= 80,
                'can_accept_more': current_count < max_orders and is_available,
            },
            'availability': {
                'status': availability_status,
                'is_available_for_auto_assignments': is_available,
                'last_updated': getattr(profile, 'availability_last_changed', None).isoformat() if hasattr(profile, 'availability_last_changed') and getattr(profile, 'availability_last_changed') else None,
                'message': getattr(profile, 'availability_message', None),
            },
            'status_breakdown': status_breakdown,
            'workload_estimate': {
                'total_pages': total_pages,
                'avg_pages_per_order': round(avg_pages_per_order, 1),
                'estimated_hours': round(estimated_hours, 1),
                'estimated_days': estimated_days_to_clear,
                'urgent_orders_count': urgent_count,
            },
            'upcoming_deadlines': upcoming_deadlines_list,
            'recommendations': recommendations,
            'writer_level': {
                'name': writer_level.name if writer_level else 'None',
                'max_orders': max_orders,
            },
        })
    
    @action(
        detail=False,
        methods=['get'],
        url_path='order-requests'
    )
    def get_order_requests(self, request):
        """
        Get writer's order request status with real-time tracking.
        
        Returns comprehensive request status including:
        - Order requests (WriterOrderRequest)
        - Writer requests (WriterRequest for additional pages/slides)
        - Status updates and review information
        - Statistics and trends
        """
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get all order requests for this writer
        order_requests = (
            WriterOrderRequest.objects.filter(
                writer=profile
            )
            .select_related(
                'order',
                'order__client',
                'reviewed_by',
                'website'
            )
            .order_by('-requested_at')
        )
        
        # Also get WriterRequest (from orders app)
        writer_requests = (
            WriterRequest.objects.filter(
                requested_by_writer=request.user
            )
            .select_related('order')
            .order_by('-created_at')
        )
        
        # Combine and format requests
        requests_list = []
        
        # Process WriterOrderRequest
        for req in order_requests:
            order = req.order
            status = 'approved' if req.approved else 'pending'
            if req.approved is False and req.reviewed_by:
                status = 'rejected'
            
            requests_list.append({
                'id': req.id,
                'type': 'order_request',
                'order_id': order.id,
                'order_topic': order.topic or 'No topic',
                'order_status': order.status,
                'order_price': (
                    float(order.total_price)
                    if order.total_price else 0
                ),
                'order_pages': self._get_order_pages(order),
                'requested_at': (
                    req.requested_at.isoformat()
                    if req.requested_at else None
                ),
                'status': status,
                'reviewed_by': (
                    req.reviewed_by.username
                    if req.reviewed_by else None
                ),
                'reviewed_at': (
                    req.reviewed_at.isoformat()
                    if hasattr(req, 'reviewed_at') and req.reviewed_at
                    else None
                ),
                'reason': req.reason or '',
            })
        
        # Process WriterRequest
        for req in writer_requests:
            order = req.order
            status = getattr(req, 'status', 'pending')
            
            requests_list.append({
                'id': req.id,
                'type': 'writer_request',
                'order_id': order.id,
                'order_topic': order.topic or 'No topic',
                'order_status': order.status,
                'order_price': (
                    float(order.total_price)
                    if order.total_price else 0
                ),
                'order_pages': self._get_order_pages(order),
                'requested_at': (
                    req.created_at.isoformat()
                    if req.created_at else None
                ),
                'status': status,
                'reviewed_by': None,
                'reviewed_at': (
                    req.updated_at.isoformat()
                    if hasattr(req, 'updated_at') and req.updated_at
                    else None
                ),
                'reason': req.reason or '',
                'additional_pages': getattr(req, 'additional_pages', 0),
                'additional_slides': getattr(req, 'additional_slides', 0),
                'has_counter_offer': getattr(
                    req, 'has_counter_offer', False
                ),
            })
        
        # Sort by requested_at (most recent first)
        requests_list.sort(
            key=lambda x: x['requested_at'] or '',
            reverse=True
        )
        
        # Calculate statistics
        total_requests = len(requests_list)
        pending_requests = len([
            r for r in requests_list
            if r['status'] == 'pending'
        ])
        approved_requests = len([
            r for r in requests_list
            if r['status'] in ['approved', 'accepted']
        ])
        rejected_requests = len([
            r for r in requests_list
            if r['status'] in ['rejected', 'declined']
        ])
        
        # Get recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_requests = [
            r for r in requests_list
            if r['requested_at'] and
            r['requested_at'] >= week_ago.isoformat()
        ]
        
        return Response({
            'requests': requests_list,
            'statistics': {
                'total': total_requests,
                'pending': pending_requests,
                'approved': approved_requests,
                'rejected': rejected_requests,
                'recent_7_days': len(recent_requests),
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
    
    @action(
        detail=False,
        methods=['get'],
        url_path='earnings-breakdown'
    )
    def get_earnings_breakdown(self, request):
        """
        Get detailed earnings breakdown by source.
        
        Returns comprehensive breakdown including:
        - Regular orders earnings
        - Special orders earnings
        - Class bonuses
        - Tips
        - Other bonuses
        - Time period breakdowns
        - Trends and statistics
        """
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Import required models
        from writer_management.models.payout import WriterPayment
        from special_orders.models import WriterBonus, SpecialOrder
        from orders.models import Order
        
        # Get regular order earnings
        regular_orders = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            updated_at__gte=date_from
        ).select_related('type_of_work')
        
        regular_earnings = Decimal('0.00')
        regular_orders_list = []
        for order in regular_orders:
            # Get payment amount (admin-set or level-based)
            payment = WriterPayment.objects.filter(
                writer=profile,
                order=order
            ).first()
            if payment:
                amount = payment.amount
            else:
                # Calculate from level
                if profile.writer_level:
                    pages = self._get_order_pages(order)
                    if order.type_of_work:
                        if order.type_of_work.name == 'Slides':
                            amount = (
                                profile.writer_level.base_pay_per_slide *
                                pages
                            )
                        else:
                            amount = (
                                profile.writer_level.base_pay_per_page *
                                pages
                            )
                    else:
                        amount = (
                            profile.writer_level.base_pay_per_page *
                            pages
                        )
                else:
                    amount = Decimal('0.00')
            
            regular_earnings += amount
            regular_orders_list.append({
                'order_id': order.id,
                'topic': order.topic or 'No topic',
                'amount': float(amount),
                'pages': self._get_order_pages(order),
                'completed_at': (
                    order.updated_at.isoformat()
                    if order.updated_at else None
                ),
            })
        
        # Get special order earnings
        special_orders = SpecialOrder.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            updated_at__gte=date_from
        )
        
        special_earnings = Decimal('0.00')
        special_orders_list = []
        for so in special_orders:
            # Use admin-set payment or calculate
            if so.writer_payment_amount:
                amount = so.writer_payment_amount
            elif so.writer_payment_percentage and so.total_cost:
                amount = (
                    so.total_cost *
                    Decimal(str(so.writer_payment_percentage)) / 100
                )
            else:
                amount = Decimal('0.00')
            
            special_earnings += amount
            special_orders_list.append({
                'order_id': so.id,
                'topic': so.topic or 'No topic',
                'amount': float(amount),
                'total_cost': float(so.total_cost or 0),
                'completed_at': (
                    so.updated_at.isoformat()
                    if so.updated_at else None
                ),
            })
        
        # Get class bonuses
        class_bonuses = WriterBonus.objects.filter(
            writer=request.user,
            category='class_payment',
            granted_at__gte=date_from
        )
        
        class_earnings = (
            class_bonuses.aggregate(Sum('amount'))['amount__sum']
            or Decimal('0.00')
        )
        class_bonuses_list = [
            {
                'id': cb.id,
                'class_id': cb.special_order.id if cb.special_order else None,
                'amount': float(cb.amount),
                'granted_at': (
                    cb.granted_at.isoformat()
                    if cb.granted_at else None
                ),
                'description': cb.description or '',
            }
            for cb in class_bonuses
        ]
        
        # Get tips
        tips_payments = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=date_from
        ).exclude(description__icontains='installment')
        
        tips_total = (
            tips_payments.aggregate(Sum('tips'))['tips__sum']
            or Decimal('0.00')
        )
        
        # Get other bonuses (excluding class bonuses)
        bonuses_total = (
            tips_payments.aggregate(Sum('bonuses'))['bonuses__sum']
            or Decimal('0.00')
        )
        
        # Calculate totals
        total_earnings = (
            regular_earnings +
            special_earnings +
            class_earnings +
            tips_total +
            bonuses_total
        )
        
        # Time period breakdown
        week_start = timezone.now() - timedelta(days=7)
        month_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        
        # Weekly breakdown
        week_regular = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            updated_at__gte=week_start
        ).count()
        
        week_special = SpecialOrder.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            updated_at__gte=week_start
        ).count()
        
        week_class = WriterBonus.objects.filter(
            writer=request.user,
            category='class_payment',
            granted_at__gte=week_start
        ).count()
        
        # Monthly breakdown
        month_regular = Order.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            updated_at__gte=month_start
        ).count()
        
        month_special = SpecialOrder.objects.filter(
            assigned_writer=request.user,
            status__in=['completed', 'approved'],
            updated_at__gte=month_start
        ).count()
        
        month_class = WriterBonus.objects.filter(
            writer=request.user,
            category='class_payment',
            granted_at__gte=month_start
        ).count()
        
        return Response({
            'summary': {
                'total_earnings': float(total_earnings),
                'regular_orders': float(regular_earnings),
                'special_orders': float(special_earnings),
                'class_bonuses': float(class_earnings),
                'tips': float(tips_total),
                'other_bonuses': float(bonuses_total),
            },
            'breakdown': {
                'regular_orders': {
                    'total': float(regular_earnings),
                    'count': len(regular_orders_list),
                    'average': (
                        float(regular_earnings / len(regular_orders_list))
                        if regular_orders_list else 0.0
                    ),
                    'orders': regular_orders_list,
                },
                'special_orders': {
                    'total': float(special_earnings),
                    'count': len(special_orders_list),
                    'average': (
                        float(special_earnings / len(special_orders_list))
                        if special_orders_list else 0.0
                    ),
                    'orders': special_orders_list,
                },
                'class_bonuses': {
                    'total': float(class_earnings),
                    'count': len(class_bonuses_list),
                    'average': (
                        float(class_earnings / len(class_bonuses_list))
                        if class_bonuses_list else 0.0
                    ),
                    'bonuses': class_bonuses_list,
                },
                'tips': {
                    'total': float(tips_total),
                    'count': tips_payments.filter(
                        tips__gt=0
                    ).count(),
                },
                'other_bonuses': {
                    'total': float(bonuses_total),
                },
            },
            'time_periods': {
                'this_week': {
                    'regular_orders': week_regular,
                    'special_orders': week_special,
                    'class_bonuses': week_class,
                },
                'this_month': {
                    'regular_orders': month_regular,
                    'special_orders': month_special,
                    'class_bonuses': month_class,
                },
            },
            'date_range': {
                'from': date_from.isoformat(),
                'to': timezone.now().isoformat(),
                'days': days,
            },
        })
    
    @action(
        detail=False,
        methods=['get'],
        url_path='earnings-export'
    )
    def export_earnings(self, request):
        """
        Export earnings history to CSV format.
        
        Returns CSV file with all earnings for tax purposes.
        Includes: date, type, amount, description, order_id
        """
        from django.http import HttpResponse
        import csv
        from io import StringIO
        
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get date range from query params
        days = int(request.query_params.get('days', 365))
        date_from = timezone.now() - timedelta(days=days)
        format_type = request.query_params.get('format', 'csv')
        
        # Import required models
        from writer_management.models.payout import WriterPayment
        from special_orders.models import WriterBonus, SpecialOrder
        from orders.models import Order
        
        # Collect all earnings records
        earnings_records = []
        
        # Regular order payments
        payments = WriterPayment.objects.filter(
            writer=profile,
            payment_date__gte=date_from
        ).exclude(description__icontains='installment')
        
        for payment in payments:
            earnings_records.append({
                'date': payment.payment_date,
                'type': 'Regular Order',
                'amount': payment.amount,
                'description': payment.description or 'Order payment',
                'order_id': (
                    payment.order.id
                    if hasattr(payment, 'order') and payment.order
                    else None
                ),
            })
            
            # Add tips and bonuses as separate records
            if payment.tips and payment.tips > 0:
                earnings_records.append({
                    'date': payment.payment_date,
                    'type': 'Tip',
                    'amount': payment.tips,
                    'description': 'Client tip',
                    'order_id': (
                        payment.order.id
                        if hasattr(payment, 'order') and payment.order
                        else None
                    ),
                })
            
            if payment.bonuses and payment.bonuses > 0:
                earnings_records.append({
                    'date': payment.payment_date,
                    'type': 'Bonus',
                    'amount': payment.bonuses,
                    'description': 'Performance bonus',
                    'order_id': (
                        payment.order.id
                        if hasattr(payment, 'order') and payment.order
                        else None
                    ),
                })
        
        # Class bonuses
        class_bonuses = WriterBonus.objects.filter(
            writer=request.user,
            category='class_payment',
            granted_at__gte=date_from
        )
        
        for bonus in class_bonuses:
            earnings_records.append({
                'date': bonus.granted_at,
                'type': 'Class Payment',
                'amount': bonus.amount,
                'description': (
                    bonus.description or 'Class completion bonus'
                ),
                'order_id': (
                    bonus.special_order.id
                    if bonus.special_order else None
                ),
            })
        
        # Sort by date
        earnings_records.sort(key=lambda x: x['date'])
        
        # Generate CSV
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            filename = (
                f'earnings_export_{profile.user.username}_'
                f'{date_from.strftime("%Y%m%d")}_'
                f'{timezone.now().strftime("%Y%m%d")}.csv'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{filename}"'
            )
            
            writer = csv.writer(response)
            writer.writerow([
                'Date',
                'Type',
                'Amount',
                'Description',
                'Order ID',
            ])
            
            total = Decimal('0.00')
            for record in earnings_records:
                writer.writerow([
                    record['date'].strftime('%Y-%m-%d'),
                    record['type'],
                    f"{record['amount']:.2f}",
                    record['description'],
                    record['order_id'] or '',
                ])
                total += Decimal(str(record['amount']))
            
            # Add summary row
            writer.writerow([])
            writer.writerow(['Total', '', f"{total:.2f}", '', ''])
            
            return response
        else:
            # Return JSON format
            return Response({
                'earnings': [
                    {
                        'date': r['date'].isoformat(),
                        'type': r['type'],
                        'amount': float(r['amount']),
                        'description': r['description'],
                        'order_id': r['order_id'],
                    }
                    for r in earnings_records
                ],
                'total': float(
                    sum(Decimal(str(r['amount'])) for r in earnings_records)
                ),
                'date_range': {
                    'from': date_from.isoformat(),
                    'to': timezone.now().isoformat(),
                },
            })
    
    @action(
        detail=False,
        methods=['get', 'post', 'patch'],
        url_path='order-priority/(?P<order_id>[0-9]+)'
    )
    def order_priority(self, request, order_id=None):
        """
        Get or set priority for a specific order.
        
        GET: Retrieve priority for an order
        POST/PATCH: Set or update priority
        """
        from writer_management.models.order_priority import (
            WriterOrderPriority
        )
        from orders.models import Order
        
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Verify order exists and is assigned to writer
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=404
            )
        
        if order.assigned_writer != request.user:
            return Response(
                {"detail": "Order not assigned to you."},
                status=403
            )
        
        if request.method == 'GET':
            # Get existing priority
            try:
                priority_obj = WriterOrderPriority.objects.get(
                    writer=request.user,
                    order=order
                )
                return Response({
                    'order_id': order.id,
                    'priority': priority_obj.priority,
                    'notes': priority_obj.notes,
                    'created_at': (
                        priority_obj.created_at.isoformat()
                        if priority_obj.created_at else None
                    ),
                    'updated_at': (
                        priority_obj.updated_at.isoformat()
                        if priority_obj.updated_at else None
                    ),
                })
            except WriterOrderPriority.DoesNotExist:
                return Response({
                    'order_id': order.id,
                    'priority': 'medium',
                    'notes': None,
                    'created_at': None,
                    'updated_at': None,
                })
        
        # POST/PATCH: Set or update priority
        priority = request.data.get('priority', 'medium')
        notes = request.data.get('notes', '')
        
        if priority not in ['high', 'medium', 'low']:
            return Response(
                {"detail": "Priority must be high, medium, or low."},
                status=400
            )
        
        priority_obj, created = (
            WriterOrderPriority.objects.update_or_create(
                writer=request.user,
                order=order,
                defaults={
                    'priority': priority,
                    'notes': notes[:500] if notes else '',
                }
            )
        )
        
        return Response({
            'order_id': order.id,
            'priority': priority_obj.priority,
            'notes': priority_obj.notes,
            'created_at': (
                priority_obj.created_at.isoformat()
                if priority_obj.created_at else None
            ),
            'updated_at': (
                priority_obj.updated_at.isoformat()
                if priority_obj.updated_at else None
            ),
            'created': created,
        }, status=201 if created else 200)
    
    @action(
        detail=False,
        methods=['get'],
        url_path='order-priorities'
    )
    def get_order_priorities(self, request):
        """
        Get all priorities for writer's orders.
        
        Returns a map of order_id -> priority for quick lookup.
        """
        from writer_management.models.order_priority import (
            WriterOrderPriority
        )
        from orders.models import Order
        
        profile = self.get_writer_profile(request)
        if not profile:
            return Response(
                {"detail": "Writer profile not found."},
                status=404
            )
        
        # Get all orders assigned to writer
        orders = Order.objects.filter(
            assigned_writer=request.user
        ).values_list('id', flat=True)
        
        # Get priorities
        priorities = WriterOrderPriority.objects.filter(
            writer=request.user,
            order_id__in=orders
        ).select_related('order')
        
        priority_map = {}
        for p in priorities:
            priority_map[p.order_id] = {
                'priority': p.priority,
                'notes': p.notes,
                'updated_at': (
                    p.updated_at.isoformat()
                    if p.updated_at else None
                ),
            }
        
        # Add default 'medium' for orders without priority
        for order_id in orders:
            if order_id not in priority_map:
                priority_map[order_id] = {
                    'priority': 'medium',
                    'notes': None,
                    'updated_at': None,
                }
        
        return Response({
            'priorities': priority_map,
            'total_orders': len(orders),
            'prioritized': len([
                p for p in priority_map.values()
                if p['priority'] != 'medium'
            ]),
        })
    
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

    def _serialize_availability(self, profile):
        return {
            "is_available": bool(getattr(profile, 'is_available_for_auto_assignments', True)),
            "message": profile.availability_message or "",
            "last_changed": profile.availability_last_changed.isoformat()
            if getattr(profile, 'availability_last_changed', None) else None,
        }

