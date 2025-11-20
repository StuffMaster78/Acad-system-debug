from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from client_management.models import ClientProfile
from orders.models import Order
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
    def get_stats(self, request):
        """Get comprehensive client dashboard statistics."""
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
    def get_loyalty(self, request):
        """Get loyalty points summary and tier information."""
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
    def get_analytics(self, request):
        """Get order and spending analytics."""
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
        
        # Service type breakdown
        service_breakdown = Order.objects.filter(
            client=request.user,
            created_at__gte=date_from
        ).values('service_type').annotate(
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
                    'service_type': item['service_type'] or 'Unknown',
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

