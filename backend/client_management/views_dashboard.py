from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.utils.cache_helpers import cache_view_result

from client_management.models import ClientProfile
from orders.models import Order, WriterProgress, OrderTransitionLog, WriterReassignmentLog
from order_payments_management.models import OrderPayment
from wallet.models import Wallet, WalletTransaction
from loyalty_management.models import LoyaltyTransaction, LoyaltyTier, ClientBadge
try:
    from referrals.models import Referral
except ImportError:
    Referral = None


class ClientDashboardViewSet(viewsets.ViewSet):
    """API for client dashboard statistics and analytics."""
    permission_classes = [IsAuthenticated]

    def get_client_profile(self, request):
        """Get the client profile for the current user."""
        if request.user.role != 'client':
            return None
        try:
            return request.user.client_profile
        except ClientProfile.DoesNotExist:
            return None

    @action(detail=False, methods=['get'], url_path='stats')
    @cache_view_result(timeout=300, key_prefix='client_dashboard')  # 5 minute cache
    def get_stats(self, request):
        """Get comprehensive client dashboard statistics - with caching."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get client's orders
        orders = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from
        )
        
        # Get payments
        payments = OrderPayment.objects.filter(
            order__client=request.user,
            order__created_at__gte=date_from,
            status='completed'
        )
        
        # Order statistics - combined query
        orders_by_status = orders.values('status').annotate(count=Count('id'))
        status_breakdown = {item['status']: item['count'] for item in orders_by_status}
        total_orders = sum(item['count'] for item in orders_by_status)
        
        # Revenue statistics - combined into single aggregation
        payment_stats = payments.aggregate(
            total_spend=Sum('amount'),
            avg_order_value=Avg('amount'),
            paid_orders_count=Count('id')
        )
        total_spend = payment_stats['total_spend'] or Decimal('0.00')
        avg_order_value = payment_stats['avg_order_value'] or Decimal('0.00')
        paid_orders_count = payment_stats['paid_orders_count'] or 0
        
        # All-time statistics - combined queries
        all_time_orders_qs = Order.objects.filter(client=request.user)
        all_time_payments_qs = OrderPayment.objects.filter(
            order__client=request.user,
            status='completed'
        )
        all_time_stats = all_time_orders_qs.aggregate(
            total_orders=Count('id')
        )
        all_time_payment_stats = all_time_payments_qs.aggregate(
            total_spend=Sum('amount')
        )
        all_time_orders = all_time_stats['total_orders'] or 0
        all_time_spend = all_time_payment_stats['total_spend'] or Decimal('0.00')
        
        # This month statistics - combined queries
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_orders_qs = Order.objects.filter(
            client=request.user,
            created_at__gte=month_start
        )
        month_payments_qs = OrderPayment.objects.filter(
            order__client=request.user,
            created_at__gte=month_start,
            status='completed'
        )
        month_stats = month_orders_qs.aggregate(
            total_orders=Count('id')
        )
        month_payment_stats = month_payments_qs.aggregate(
            total_spend=Sum('amount')
        )
        month_orders = month_stats['total_orders'] or 0
        month_spend = month_payment_stats['total_spend'] or Decimal('0.00')
        
        # This year statistics - combined queries
        year_start = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        year_orders_qs = Order.objects.filter(
            client=request.user,
            created_at__gte=year_start
        )
        year_payments_qs = OrderPayment.objects.filter(
            order__client=request.user,
            created_at__gte=year_start,
            status='completed'
        )
        year_stats = year_orders_qs.aggregate(
            total_orders=Count('id')
        )
        year_payment_stats = year_payments_qs.aggregate(
            total_spend=Sum('amount')
        )
        year_orders = year_stats['total_orders'] or 0
        year_spend = year_payment_stats['total_spend'] or Decimal('0.00')
        
        return Response({
            'total_orders': total_orders,
            'orders_by_status': status_breakdown,
            'total_spend': float(total_spend),
            'avg_order_value': float(avg_order_value),
            'paid_orders_count': paid_orders_count,
            'unpaid_orders_count': total_orders - paid_orders_count,
            'all_time': {
                'orders': all_time_orders,
                'spend': float(all_time_spend),
            },
            'this_month': {
                'orders': month_orders,
                'spend': float(month_spend),
            },
            'this_year': {
                'orders': year_orders,
                'spend': float(year_spend),
            },
        })
    
    @action(detail=False, methods=['get'], url_path='loyalty')
    @cache_view_result(timeout=300, key_prefix='client_dashboard')  # 5 minute cache
    def get_loyalty(self, request):
        """Get loyalty points summary and tier information - with caching."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        # Get current tier
        current_tier = profile.tier
        tier_name = current_tier.name if current_tier else 'None'
        
        # Get next tier
        next_tier = None
        points_to_next = 0
        if current_tier:
            next_tier = LoyaltyTier.objects.filter(
                points_required__gt=profile.loyalty_points
            ).order_by('points_required').first()
            if next_tier:
                points_to_next = next_tier.points_required - profile.loyalty_points
        
        # Get recent transactions
        recent_transactions = LoyaltyTransaction.objects.filter(
            client=profile
        ).order_by('-timestamp')[:10]
        
        # Get badges
        badges = ClientBadge.objects.filter(client=profile).order_by('-awarded_at')
        
        # Get points earned this month
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_transactions = LoyaltyTransaction.objects.filter(
            client=profile,
            timestamp__gte=month_start,
            transaction_type='earned'
        )
        points_earned_this_month = month_transactions.aggregate(
            Sum('points')
        )['points__sum'] or 0
        
        return Response({
            'loyalty_points': profile.loyalty_points,
            'current_tier': {
                'name': tier_name,
                'id': current_tier.id if current_tier else None,
            },
            'next_tier': {
                'name': next_tier.name if next_tier else None,
                'points_required': next_tier.points_required if next_tier else None,
            },
            'points_to_next_tier': points_to_next,
            'points_earned_this_month': points_earned_this_month,
            'recent_transactions': [
                {
                    'id': t.id,
                    'points': t.points,
                    'transaction_type': t.transaction_type,
                    'reason': t.reason,
                    'timestamp': t.timestamp.isoformat() if t.timestamp else None,
                }
                for t in recent_transactions
            ],
            'badges': [
                {
                    'id': b.id,
                    'badge_name': b.badge_name,
                    'awarded_at': b.awarded_at.isoformat() if b.awarded_at else None,
                }
                for b in badges
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    @cache_view_result(timeout=300, key_prefix='client_dashboard')  # 5 minute cache
    def get_analytics(self, request):
        """Get order and spending analytics - with caching."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Order trends (daily)
        orders_trend = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            total_spend=Sum('payments__amount', filter=Q(payments__status='completed'))
        ).order_by('date')
        
        # Spending trends (daily)
        spending_trend = OrderPayment.objects.filter(
            order__client=request.user,
            order__created_at__gte=date_from,
            status='completed'
        ).annotate(
            date=TruncDate('order__created_at')
        ).values('date').annotate(
            total=Sum('amount'),
            count=Count('order', distinct=True)
        ).order_by('date')
        
        # Service type breakdown (using type_of_work)
        service_breakdown = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from
        ).values('type_of_work__name').annotate(
            count=Count('id'),
            total_spend=Sum('payments__amount', filter=Q(payments__status='completed'))
        ).order_by('-count')
        
        # Average completion time (if orders have completion dates)
        completed_orders = Order.objects.filter(
            client=request.user,
            status='completed',
            created_at__gte=date_from
        )
        
        # Calculate average days to completion
        avg_completion_days = None
        if completed_orders.exists():
            completion_times = []
            for order in completed_orders:
                # Check if order has completed_at field
                completed_at = getattr(order, 'completed_at', None)
                if completed_at and order.created_at:
                    days = (completed_at - order.created_at).days
                    if days >= 0:  # Only count positive days
                        completion_times.append(days)
            if completion_times:
                avg_completion_days = sum(completion_times) / len(completion_times)
        
        # Revision rate
        total_orders_count = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from
        ).count()
        revised_orders = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from,
            status='on_revision'
        ).count()
        revision_rate = (revised_orders / total_orders_count * 100) if total_orders_count > 0 else 0
        
        return Response({
            'order_trends': [
                {
                    'date': item['date'].isoformat() if item['date'] else None,
                    'count': item['count'],
                    'spend': float(item['total_spend'] or 0),
                }
                for item in orders_trend
            ],
            'spending_trends': [
                {
                    'date': item['date'].isoformat() if item['date'] else None,
                    'total': float(item['total'] or 0),
                    'order_count': item['count'],
                }
                for item in spending_trend
            ],
            'service_breakdown': [
                {
                    'service_type': item['type_of_work__name'] or 'Unknown',
                    'count': item['count'],
                    'total_spend': float(item['total_spend'] or 0),
                }
                for item in service_breakdown
            ],
            'avg_completion_days': avg_completion_days,
            'revision_rate': revision_rate,
        })
    
    @action(detail=False, methods=['get'], url_path='wallet')
    def get_wallet_analytics(self, request):
        """Get wallet analytics and transaction history."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response({
                'balance': 0,
                'transactions': [],
                'top_up_history': [],
                'spending_breakdown': {},
            })
        
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get transactions
        transactions = WalletTransaction.objects.filter(
            wallet=wallet,
            created_at__gte=date_from
        ).order_by('-created_at')
        
        # Get top-up history
        top_ups = transactions.filter(transaction_type='credit').order_by('-created_at')
        
        # Spending breakdown by category
        spending = transactions.filter(transaction_type='debit')
        spending_breakdown = spending.values('description').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        return Response({
            'balance': float(wallet.balance),
            'transactions': [
                {
                    'id': t.id,
                    'amount': float(t.amount),
                    'transaction_type': t.transaction_type,
                    'description': t.description,
                    'created_at': t.created_at.isoformat() if t.created_at else None,
                }
                for t in transactions[:50]  # Limit to 50 most recent
            ],
            'top_up_history': [
                {
                    'id': t.id,
                    'amount': float(t.amount),
                    'created_at': t.created_at.isoformat() if t.created_at else None,
                }
                for t in top_ups[:20]
            ],
            'spending_breakdown': {
                item['description'] or 'Other': float(item['total'])
                for item in spending_breakdown
            },
        })
    
    @action(detail=False, methods=['get'], url_path='referrals')
    def get_referrals(self, request):
        """Get referral dashboard data."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        if not Referral:
            return Response({
                'total_referrals': 0,
                'successful_referrals': 0,
                'pending_referrals': 0,
                'referral_earnings': 0.0,
                'referral_link': None,
                'recent_referrals': [],
            })
        
        # Get client's referrals (exclude deleted)
        referrals = Referral.objects.filter(referrer=request.user, is_deleted=False)
        
        # Get referral stats
        total_referrals = referrals.count()
        # Successful referrals are those where bonus has been awarded
        successful_referrals = referrals.filter(bonus_awarded=True).count()
        # Pending referrals are those where bonus hasn't been awarded yet
        pending_referrals = referrals.filter(bonus_awarded=False).count()
        
        # Get referral earnings - calculate from wallet transactions or referral bonus usage
        # For now, we'll use a placeholder since there's no direct reward_amount field
        referral_earnings = Decimal('0.00')
        try:
            from referrals.models import ReferralBonusUsage
            bonus_usages = ReferralBonusUsage.objects.filter(
                referral__referrer=request.user
            ).aggregate(
                total=Sum('discount_amount')
            )
            referral_earnings = bonus_usages['total'] or Decimal('0.00')
        except Exception:
            pass
        
        # Get referral link (if exists)
        referral_link = None
        try:
            from referrals.models import ReferralCode
            referral_code_obj = ReferralCode.objects.filter(user=request.user).first()
            if referral_code_obj:
                referral_link = f"/refer/{referral_code_obj.code}"
        except Exception:
            pass
        
        return Response({
            'total_referrals': total_referrals,
            'successful_referrals': successful_referrals,
            'pending_referrals': pending_referrals,
            'referral_earnings': float(referral_earnings),
            'referral_link': referral_link,
            'recent_referrals': [
                {
                    'id': r.id,
                    'referred_user': r.referee.username if r.referee else None,
                    'status': 'completed' if r.bonus_awarded else 'pending',
                    'bonus_awarded': r.bonus_awarded,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                }
                for r in referrals[:10]
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='order-activity-timeline')
    def get_order_activity_timeline(self, request):
        """Get comprehensive activity timeline for client's orders."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        # Get order ID if specified, otherwise get all orders
        order_id = request.query_params.get('order_id', None)
        days = int(request.query_params.get('days', 90))
        date_from = timezone.now() - timedelta(days=days)
        
        # Get orders
        orders_query = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from
        )
        
        if order_id:
            orders_query = orders_query.filter(id=order_id)
        
        orders = orders_query.select_related(
            'assigned_writer', 'type_of_work', 'paper_type'
        ).prefetch_related('transitions')
        
        # Build timeline
        timeline = []
        
        for order in orders:
            # Order creation
            timeline.append({
                'order_id': order.id,
                'order_topic': order.topic or 'No topic',
                'timestamp': order.created_at.isoformat() if order.created_at else None,
                'event_type': 'order_created',
                'event_title': 'Order Created',
                'event_description': f'Order #{order.id} was created',
                'status': order.status,
                'actor': order.client.username if order.client else 'System',
            })
            
            # Status transitions
            transitions = order.transitions.all().order_by('timestamp')
            for transition in transitions:
                timeline.append({
                    'order_id': order.id,
                    'order_topic': order.topic or 'No topic',
                    'timestamp': transition.timestamp.isoformat() if transition.timestamp else None,
                    'event_type': 'status_change',
                    'event_title': f'Status Changed: {transition.old_status} → {transition.new_status}',
                    'event_description': transition.action or f'Status changed from {transition.old_status} to {transition.new_status}',
                    'old_status': transition.old_status,
                    'new_status': transition.new_status,
                    'status': transition.new_status,
                    'is_automatic': transition.is_automatic,
                    'actor': transition.user.username if transition.user else ('System' if transition.is_automatic else 'Unknown'),
                    'meta': transition.meta,
                })
            
            # Payment events
            payments = OrderPayment.objects.filter(order=order).order_by('created_at')
            for payment in payments:
                timeline.append({
                    'order_id': order.id,
                    'order_topic': order.topic or 'No topic',
                    'timestamp': payment.created_at.isoformat() if payment.created_at else None,
                    'event_type': 'payment',
                    'event_title': f'Payment {payment.status.title()}',
                    'event_description': f'Payment of ${payment.amount} - {payment.status}',
                    'status': order.status,
                    'payment_amount': float(payment.amount),
                    'payment_status': payment.status,
                    'actor': order.client.username if order.client else 'System',
                })
            
            # Writer assignment
            if order.assigned_writer:
                # Try to find when writer was assigned (could be from transitions or created_at)
                assignment_time = order.updated_at if hasattr(order, 'updated_at') else order.created_at
                timeline.append({
                    'order_id': order.id,
                    'order_topic': order.topic or 'No topic',
                    'timestamp': assignment_time.isoformat() if assignment_time else None,
                    'event_type': 'writer_assigned',
                    'event_title': 'Writer Assigned',
                    'event_description': f'Writer {order.assigned_writer.username} was assigned to this order',
                    'status': order.status,
                    'writer_id': order.assigned_writer.id,
                    'writer_username': order.assigned_writer.username,
                    'actor': 'System',
                })
            
            # Submission
            if order.submitted_at:
                timeline.append({
                    'order_id': order.id,
                    'order_topic': order.topic or 'No topic',
                    'timestamp': order.submitted_at.isoformat() if order.submitted_at else None,
                    'event_type': 'submitted',
                    'event_title': 'Order Submitted',
                    'event_description': 'Writer submitted the completed order',
                    'status': order.status,
                    'actor': order.assigned_writer.username if order.assigned_writer else 'Writer',
                })
            
            # Deadlines
            if order.client_deadline:
                timeline.append({
                    'order_id': order.id,
                    'order_topic': order.topic or 'No topic',
                    'timestamp': order.client_deadline.isoformat() if order.client_deadline else None,
                    'event_type': 'deadline',
                    'event_title': 'Client Deadline',
                    'event_description': f'Client deadline: {order.client_deadline.strftime("%Y-%m-%d %H:%M")}',
                    'status': order.status,
                    'is_overdue': order.client_deadline < timezone.now() if order.client_deadline else False,
                    'actor': 'System',
                })
        
        # Sort timeline by timestamp (most recent first)
        timeline.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        # Group by date for easier frontend rendering
        timeline_by_date = {}
        for event in timeline:
            if event['timestamp']:
                date_key = event['timestamp'][:10]  # Extract date part (YYYY-MM-DD)
                if date_key not in timeline_by_date:
                    timeline_by_date[date_key] = []
                timeline_by_date[date_key].append(event)
        
        return Response({
            'timeline': timeline,
            'timeline_by_date': timeline_by_date,
            'total_events': len(timeline),
            'date_range': {
                'from': date_from.isoformat(),
                'to': timezone.now().isoformat(),
            },
            'order_id': order_id,
        })
    
    @action(detail=False, methods=['get'], url_path='enhanced-order-status')
    def get_enhanced_order_status(self, request):
        """Get detailed order status with progress tracking, estimated completion, and quality metrics."""
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response(
                {"detail": "order_id parameter is required."},
                status=400
            )
        
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Build query based on user role
        order_query = {'id': order_id}
        
        if user_role == 'client':
            # Clients can only see their own orders
            order_query['client'] = user
        elif user_role == 'writer':
            # Writers can see orders they're assigned to or have requested
            from writer_management.models.requests import WriterOrderRequest
            try:
                writer_profile = user.writer_profile
                requested_orders = WriterOrderRequest.objects.filter(
                    writer=writer_profile
                ).values_list('order_id', flat=True)
                
                # Use Q object to check if order is assigned to writer OR requested by writer
                from django.db.models import Q
                order = Order.objects.select_related(
                    'assigned_writer', 'type_of_work', 'paper_type', 'subject',
                    'completed_by', 'client'
                ).prefetch_related(
                    'progress_logs', 'transitions', 'reassignment_logs',
                    'disputes', 'reviews'
                ).filter(
                    Q(id=order_id) & (
                        Q(assigned_writer=user) |
                        Q(id__in=requested_orders)
                    )
                ).first()
                
                if not order:
                    return Response(
                        {"detail": "Order not found or you don't have permission to view it."},
                        status=404
                    )
            except Exception:
                return Response(
                    {"detail": "Order not found or you don't have permission to view it."},
                    status=404
                )
        elif user_role in ['admin', 'superadmin', 'support', 'editor']:
            # Admins, superadmins, support, and editors can see any order
            order_query = {'id': order_id}
        else:
            return Response(
                {"detail": "You don't have permission to access this endpoint."},
                status=403
            )
        
        # For clients and admins, use the original query
        if user_role != 'writer':
            try:
                order = Order.objects.select_related(
                    'assigned_writer', 'type_of_work', 'paper_type', 'subject',
                    'completed_by', 'client'
                ).prefetch_related(
                    'progress_logs', 'transitions', 'reassignment_logs',
                    'disputes', 'reviews'
                ).get(**order_query)
            except Order.DoesNotExist:
                return Response(
                    {"detail": "Order not found."},
                    status=404
                )
        
        now = timezone.now()
        
        # Calculate progress percentage from WriterProgress logs
        progress_logs = order.progress_logs.filter(is_withdrawn=False).order_by('-timestamp')
        current_progress = 0
        if progress_logs.exists():
            latest_progress = progress_logs.first()
            current_progress = latest_progress.progress_percentage
        
        # Estimate completion time
        estimated_completion = None
        if order.assigned_writer and order.writer_deadline:
            time_remaining = order.writer_deadline - now
            if time_remaining.total_seconds() > 0:
                estimated_completion = {
                    'deadline': order.writer_deadline.isoformat(),
                    'hours_remaining': round(time_remaining.total_seconds() / 3600, 2),
                    'days_remaining': round(time_remaining.total_seconds() / 86400, 2),
                    'is_overdue': False,
                }
            else:
                estimated_completion = {
                    'deadline': order.writer_deadline.isoformat(),
                    'hours_remaining': 0,
                    'days_remaining': 0,
                    'is_overdue': True,
                }
        elif order.client_deadline:
            time_remaining = order.client_deadline - now
            if time_remaining.total_seconds() > 0:
                estimated_completion = {
                    'deadline': order.client_deadline.isoformat(),
                    'hours_remaining': round(time_remaining.total_seconds() / 3600, 2),
                    'days_remaining': round(time_remaining.total_seconds() / 86400, 2),
                    'is_overdue': False,
                }
            else:
                estimated_completion = {
                    'deadline': order.client_deadline.isoformat(),
                    'hours_remaining': 0,
                    'days_remaining': 0,
                    'is_overdue': True,
                }
        
        # Writer activity status
        writer_activity = None
        if order.assigned_writer:
            # Get last progress update
            last_progress = progress_logs.first()
            last_activity_time = None
            if last_progress:
                last_activity_time = last_progress.timestamp
            elif order.updated_at:
                last_activity_time = order.updated_at
            
            # Determine activity status
            is_active = False
            if last_activity_time:
                hours_since_activity = (now - last_activity_time).total_seconds() / 3600
                is_active = hours_since_activity < 24  # Active if activity within 24 hours
            
            writer_activity = {
                'writer_id': order.assigned_writer.id,
                'writer_username': order.assigned_writer.username,
                'is_active': is_active,
                'last_activity': last_activity_time.isoformat() if last_activity_time else None,
                'hours_since_activity': round((now - last_activity_time).total_seconds() / 3600, 2) if last_activity_time else None,
            }
        
        # Revision history
        revision_history = []
        transitions = order.transitions.filter(
            new_status__in=['revision_requested', 'on_revision', 'revised', 'revision_in_progress']
        ).order_by('timestamp')
        
        for transition in transitions:
            revision_history.append({
                'timestamp': transition.timestamp.isoformat(),
                'status': transition.new_status,
                'action': transition.action,
                'is_automatic': transition.is_automatic,
                'actor': transition.user.username if transition.user else 'System',
            })
        
        # Quality metrics
        quality_metrics = {
            'revision_count': len(revision_history),
            'dispute_count': order.disputes.count(),
            'has_reviews': order.reviews.exists(),
            'average_rating': None,
        }
        
        # Get average rating if reviews exist
        if order.reviews.exists():
            try:
                from reviews_system.models import OrderReview
                reviews = OrderReview.objects.filter(order=order)
                if reviews.exists():
                    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
                    quality_metrics['average_rating'] = round(avg_rating, 2) if avg_rating else None
            except Exception:
                pass
        
        # Recent progress updates
        recent_progress = []
        for progress in progress_logs[:5]:  # Last 5 progress updates
            recent_progress.append({
                'timestamp': progress.timestamp.isoformat(),
                'progress_percentage': progress.progress_percentage,
                'notes': progress.notes,
            })
        
        # Status timeline
        status_timeline = []
        all_transitions = order.transitions.all().order_by('timestamp')
        for transition in all_transitions:
            status_timeline.append({
                'timestamp': transition.timestamp.isoformat(),
                'from_status': transition.old_status,
                'to_status': transition.new_status,
                'action': transition.action,
                'is_automatic': transition.is_automatic,
                'actor': transition.user.username if transition.user else 'System',
            })
        
        # Writer reassignments
        reassignments = []
        for reassignment in order.reassignment_logs.all().order_by('-created_at'):
            reassignments.append({
                'timestamp': reassignment.created_at.isoformat(),
                'previous_writer': reassignment.previous_writer.username if reassignment.previous_writer else None,
                'new_writer': reassignment.new_writer.username if reassignment.new_writer else None,
                'reason': reassignment.reason,
                'reassigned_by': reassignment.reassigned_by.username if reassignment.reassigned_by else 'System',
            })
        
        return Response({
            'order_id': order.id,
            'order_topic': order.topic,
            'current_status': order.status,
            'progress': {
                'percentage': current_progress,
                'recent_updates': recent_progress,
            },
            'estimated_completion': estimated_completion,
            'writer_activity': writer_activity,
            'revision_history': revision_history,
            'quality_metrics': quality_metrics,
            'status_timeline': status_timeline,
            'writer_reassignments': reassignments,
            'deadlines': {
                'client_deadline': order.client_deadline.isoformat() if order.client_deadline else None,
                'writer_deadline': order.writer_deadline.isoformat() if order.writer_deadline else None,
            },
            'order_details': {
                'type_of_work': order.type_of_work.name if order.type_of_work else None,
                'paper_type': order.paper_type.name if order.paper_type else None,
                'number_of_pages': order.number_of_pages,
                'subject': order.subject.name if order.subject else None,
            },
        })
    
    @action(detail=False, methods=['get'], url_path='payment-reminders')
    def get_payment_reminders(self, request):
        """Get payment reminders for client's unpaid orders."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        try:
            from order_payments_management.models.payment_reminders import (
                PaymentReminderSent, PaymentReminderConfig
            )
        except ImportError:
            return Response({
                'reminders': [],
                'unpaid_orders': [],
                'message': 'Payment reminder system not available.',
            })
        
        # Get unpaid orders
        unpaid_orders = Order.objects.filter(
            client=request.user,
            is_paid=False
        ).exclude(
            status__in=['cancelled', 'refunded', 'closed']
        ).select_related('type_of_work')
        
        # Get sent reminders for these orders
        sent_reminders = PaymentReminderSent.objects.filter(
            client=request.user,
            order__in=unpaid_orders
        ).select_related('reminder_config', 'order').order_by('-sent_at')
        
        # Get reminder configurations
        reminder_configs = PaymentReminderConfig.objects.filter(
            website=request.user.website,
            is_active=True
        ).order_by('deadline_percentage')
        
        # Build reminders list
        reminders_list = []
        for reminder in sent_reminders:
            reminders_list.append({
                'id': reminder.id,
                'order_id': reminder.order.id,
                'order_topic': reminder.order.topic,
                'reminder_name': reminder.reminder_config.name,
                'deadline_percentage': float(reminder.reminder_config.deadline_percentage),
                'message': reminder.reminder_config.message,
                'sent_at': reminder.sent_at.isoformat(),
                'sent_as_notification': reminder.sent_as_notification,
                'sent_as_email': reminder.sent_as_email,
            })
        
        # Build unpaid orders list with reminder eligibility
        unpaid_orders_list = []
        for order in unpaid_orders:
            # Calculate deadline percentage
            deadline_percentage = None
            if order.client_deadline:
                now = timezone.now()
                if order.created_at:
                    total_duration = (order.client_deadline - order.created_at).total_seconds()
                    elapsed = (now - order.created_at).total_seconds()
                    if total_duration > 0:
                        deadline_percentage = (elapsed / total_duration) * 100
            
            # Check which reminders have been sent
            sent_for_order = PaymentReminderSent.objects.filter(
                order=order,
                client=request.user
            ).values_list('reminder_config__deadline_percentage', flat=True)
            
            # Find next eligible reminder
            next_reminder = None
            if deadline_percentage is not None:
                for config in reminder_configs:
                    if float(config.deadline_percentage) > deadline_percentage:
                        if float(config.deadline_percentage) not in sent_for_order:
                            next_reminder = {
                                'name': config.name,
                                'deadline_percentage': float(config.deadline_percentage),
                                'message': config.message,
                            }
                            break
            
            unpaid_orders_list.append({
                'order_id': order.id,
                'order_topic': order.topic,
                'type_of_work': order.type_of_work.name if order.type_of_work else None,
                'total_price': float(order.total_price),
                'client_deadline': order.client_deadline.isoformat() if order.client_deadline else None,
                'created_at': order.created_at.isoformat(),
                'deadline_percentage': round(deadline_percentage, 2) if deadline_percentage else None,
                'next_reminder': next_reminder,
                'reminders_sent': list(sent_for_order),
            })
        
        return Response({
            'reminders': reminders_list,
            'unpaid_orders': unpaid_orders_list,
            'total_unpaid_orders': len(unpaid_orders_list),
            'total_reminders_sent': len(reminders_list),
        })
    
    @action(detail=False, methods=['post'], url_path='payment-reminders/create')
    def create_payment_reminder_preference(self, request):
        """Create a payment reminder preference for a specific order."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        order_id = request.data.get('order_id')
        reminder_config_id = request.data.get('reminder_config_id')
        custom_message = request.data.get('custom_message')
        
        if not order_id:
            return Response(
                {"detail": "order_id is required."},
                status=400
            )
        
        try:
            order = Order.objects.get(id=order_id, client=request.user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=404
            )
        
        # Check if order is unpaid
        if order.is_paid:
            return Response(
                {"detail": "Order is already paid."},
                status=400
            )
        
        try:
            from order_payments_management.models.payment_reminders import (
                PaymentReminderConfig, PaymentReminderSent
            )
        except ImportError:
            return Response({
                'detail': 'Payment reminder system not available.',
            }, status=503)
        
        # If reminder_config_id is provided, use it; otherwise create a default preference
        if reminder_config_id:
            try:
                reminder_config = PaymentReminderConfig.objects.get(
                    id=reminder_config_id,
                    website=request.user.website,
                    is_active=True
                )
            except PaymentReminderConfig.DoesNotExist:
                return Response(
                    {"detail": "Reminder configuration not found."},
                    status=404
                )
        else:
            # Get the first active reminder config for the website
            reminder_config = PaymentReminderConfig.objects.filter(
                website=request.user.website,
                is_active=True
            ).first()
            
            if not reminder_config:
                return Response(
                    {"detail": "No active reminder configurations available."},
                    status=404
                )
        
        # Check if reminder already sent for this order and config
        existing = PaymentReminderSent.objects.filter(
            order=order,
            reminder_config=reminder_config,
            client=request.user
        ).first()
        
        if existing:
            return Response(
                {"detail": "Reminder already sent for this order and configuration."},
                status=400
            )
        
        # Create reminder sent record (this marks the preference)
        reminder_sent = PaymentReminderSent.objects.create(
            reminder_config=reminder_config,
            order=order,
            client=request.user,
            sent_as_notification=reminder_config.send_as_notification,
            sent_as_email=reminder_config.send_as_email
        )
        
        return Response({
            'id': reminder_sent.id,
            'order_id': order.id,
            'reminder_config_id': reminder_config.id,
            'reminder_name': reminder_config.name,
            'created_at': reminder_sent.sent_at.isoformat(),
            'message': 'Payment reminder preference created successfully.',
        }, status=201)
    
    @action(detail=False, methods=['patch'], url_path='payment-reminders/(?P<reminder_id>[^/.]+)/update')
    def update_payment_reminder_preference(self, request, reminder_id=None):
        """Update a payment reminder preference."""
        profile = self.get_client_profile(request)
        if not profile:
            return Response(
                {"detail": "Client profile not found."},
                status=404
            )
        
        try:
            from order_payments_management.models.payment_reminders import (
                PaymentReminderSent
            )
        except ImportError:
            return Response({
                'detail': 'Payment reminder system not available.',
            }, status=503)
        
        try:
            reminder_sent = PaymentReminderSent.objects.get(
                id=reminder_id,
                client=request.user
            )
        except PaymentReminderSent.DoesNotExist:
            return Response(
                {"detail": "Reminder preference not found."},
                status=404
            )
        
        # Update preferences if provided
        if 'reminder_config_id' in request.data:
            try:
                from order_payments_management.models.payment_reminders import PaymentReminderConfig
                new_config = PaymentReminderConfig.objects.get(
                    id=request.data['reminder_config_id'],
                    website=request.user.website,
                    is_active=True
                )
                reminder_sent.reminder_config = new_config
            except PaymentReminderConfig.DoesNotExist:
                return Response(
                    {"detail": "Reminder configuration not found."},
                    status=404
                )
        
        if 'send_as_notification' in request.data:
            reminder_sent.sent_as_notification = request.data['send_as_notification']
        
        if 'send_as_email' in request.data:
            reminder_sent.sent_as_email = request.data['send_as_email']
        
        reminder_sent.save()
        
        return Response({
            'id': reminder_sent.id,
            'order_id': reminder_sent.order.id if reminder_sent.order else None,
            'reminder_config_id': reminder_sent.reminder_config.id,
            'reminder_name': reminder_sent.reminder_config.name,
            'send_as_notification': reminder_sent.sent_as_notification,
            'send_as_email': reminder_sent.sent_as_email,
            'updated_at': reminder_sent.sent_at.isoformat(),
            'message': 'Payment reminder preference updated successfully.',
        })

