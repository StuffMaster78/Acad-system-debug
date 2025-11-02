"""
Analytics Service for Loyalty Program
Aggregates and calculates analytics data for loyalty program performance.
"""
from django.db.models import (
    Sum, Count, Avg, Max, Min, Q, F
)
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from loyalty_management.models import (
    LoyaltyTransaction,
    LoyaltyAnalytics,
    RedemptionRequest,
    RedemptionItem,
    LoyaltyTier,
    ClientBadge
)
from client_management.models import ClientProfile
from orders.models import Order


class LoyaltyAnalyticsService:
    """
    Service for calculating and aggregating loyalty program analytics.
    """
    
    @staticmethod
    def calculate_analytics(website, date_from=None, date_to=None):
        """
        Calculate analytics for a given date range.
        
        Args:
            website: Website instance
            date_from: Start date (defaults to 30 days ago)
            date_to: End date (defaults to today)
        
        Returns:
            LoyaltyAnalytics instance
        """
        if date_to is None:
            date_to = date.today()
        if date_from is None:
            date_from = date_to - timedelta(days=30)
        
        # Get or create analytics record
        analytics, created = LoyaltyAnalytics.objects.update_or_create(
            website=website,
            date_from=date_from,
            date_to=date_to,
            defaults={}
        )
        
        # Overall metrics
        analytics.total_active_clients = ClientProfile.objects.filter(
            website=website,
            loyalty_points__gt=0
        ).count()
        
        # Points metrics
        transactions = LoyaltyTransaction.objects.filter(
            website=website,
            timestamp__date__gte=date_from,
            timestamp__date__lte=date_to
        )
        
        add_transactions = transactions.filter(transaction_type='add')
        redeem_transactions = transactions.filter(transaction_type='redeem')
        
        analytics.total_points_issued = add_transactions.aggregate(
            total=Sum('points')
        )['total'] or 0
        
        analytics.total_points_redeemed = abs(redeem_transactions.aggregate(
            total=Sum('points')
        )['total'] or 0)
        
        # Current balance (sum all transactions)
        all_transactions = LoyaltyTransaction.objects.filter(website=website)
        analytics.total_points_balance = all_transactions.aggregate(
            total=Sum('points')
        )['total'] or 0
        
        # Redemption metrics
        redemptions = RedemptionRequest.objects.filter(
            website=website,
            requested_at__date__gte=date_from,
            requested_at__date__lte=date_to
        )
        
        analytics.total_redemptions = redemptions.filter(
            status='fulfilled'
        ).count()
        
        analytics.total_redemption_value = redemptions.filter(
            status='fulfilled'
        ).aggregate(
            total=Sum('points_used')
        )['total'] or 0
        
        # Most popular redemption item
        popular_item = redemptions.filter(
            status='fulfilled'
        ).values('item').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        if popular_item:
            try:
                analytics.most_popular_item = RedemptionItem.objects.get(id=popular_item['item'])
            except RedemptionItem.DoesNotExist:
                pass
        
        # Tier distribution
        tiers = LoyaltyTier.objects.filter(website=website).order_by('threshold')
        analytics.bronze_count = ClientProfile.objects.filter(
            website=website,
            tier__name__icontains='bronze'
        ).count() or 0
        analytics.silver_count = ClientProfile.objects.filter(
            website=website,
            tier__name__icontains='silver'
        ).count() or 0
        analytics.gold_count = ClientProfile.objects.filter(
            website=website,
            tier__name__icontains='gold'
        ).count() or 0
        analytics.platinum_count = ClientProfile.objects.filter(
            website=website,
            tier__name__icontains='platinum'
        ).count() or 0
        
        # Engagement metrics
        active_clients = analytics.total_active_clients
        if active_clients > 0:
            clients_who_redeemed = redemptions.filter(
                status='fulfilled'
            ).values('client').distinct().count()
            analytics.active_redemptions_ratio = (
                Decimal(clients_who_redeemed) / Decimal(active_clients) * 100
            )
            
            analytics.average_points_per_client = (
                Decimal(analytics.total_points_balance) / Decimal(active_clients)
            )
        else:
            analytics.active_redemptions_ratio = Decimal('0.00')
            analytics.average_points_per_client = Decimal('0.00')
        
        analytics.save()
        return analytics
    
    @staticmethod
    def get_points_trend(website, days=30):
        """
        Get points issued/redeemed trend over time.
        
        Returns:
            List of dicts with date, issued, redeemed, balance
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        transactions = LoyaltyTransaction.objects.filter(
            website=website,
            timestamp__date__gte=start_date,
            timestamp__date__lte=end_date
        ).extra(
            select={'day': "DATE(timestamp)"}
        ).values('day', 'transaction_type').annotate(
            total_points=Sum('points')
        )
        
        # Aggregate by day
        daily_data = {}
        for trans in transactions:
            day = trans['day']
            if day not in daily_data:
                daily_data[day] = {'issued': 0, 'redeemed': 0}
            
            if trans['transaction_type'] == 'add':
                daily_data[day]['issued'] += abs(trans['total_points'])
            elif trans['transaction_type'] == 'redeem':
                daily_data[day]['redeemed'] += abs(trans['total_points'])
        
        # Convert to list and calculate running balance
        trend = []
        balance = 0
        for day in sorted(daily_data.keys()):
            balance += daily_data[day]['issued'] - daily_data[day]['redeemed']
            trend.append({
                'date': day,
                'issued': daily_data[day]['issued'],
                'redeemed': daily_data[day]['redeemed'],
                'balance': balance
            })
        
        return trend
    
    @staticmethod
    def get_top_redemption_items(website, limit=10):
        """
        Get most popular redemption items.
        
        Returns:
            List of dicts with item info and redemption counts
        """
        items = RedemptionItem.objects.filter(
            website=website
        ).annotate(
            redemption_count=Count(
                'requests',
                filter=Q(requests__status='fulfilled')
            )
        ).order_by('-redemption_count')[:limit]
        
        return [
            {
                'id': item.id,
                'name': item.name,
                'points_required': item.points_required,
                'redemption_count': item.redemption_count,
                'category': item.category.name
            }
            for item in items
        ]
    
    @staticmethod
    def get_tier_distribution(website):
        """
        Get distribution of clients across loyalty tiers.
        
        Returns:
            Dict with tier names and counts
        """
        tiers = LoyaltyTier.objects.filter(website=website).order_by('threshold')
        
        distribution = {}
        for tier in tiers:
            count = ClientProfile.objects.filter(
                website=website,
                tier=tier
            ).count()
            distribution[tier.name] = {
                'count': count,
                'threshold': tier.threshold,
                'percentage': 0  # Will calculate if total > 0
            }
        
        # Calculate percentages
        total = sum(t['count'] for t in distribution.values())
        if total > 0:
            for tier_data in distribution.values():
                tier_data['percentage'] = (
                    Decimal(tier_data['count']) / Decimal(total) * 100
                )
        
        return distribution
    
    @staticmethod
    def get_client_engagement_stats(website, days=30):
        """
        Get client engagement statistics.
        
        Returns:
            Dict with engagement metrics
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        total_clients = ClientProfile.objects.filter(website=website).count()
        active_clients = ClientProfile.objects.filter(
            website=website,
            loyalty_points__gt=0
        ).count()
        
        clients_with_redemptions = RedemptionRequest.objects.filter(
            website=website,
            requested_at__date__gte=start_date,
            status='fulfilled'
        ).values('client').distinct().count()
        
        clients_with_transactions = LoyaltyTransaction.objects.filter(
            website=website,
            timestamp__date__gte=start_date
        ).values('client').distinct().count()
        
        return {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'clients_with_redemptions': clients_with_redemptions,
            'clients_with_transactions': clients_with_transactions,
            'engagement_rate': (
                Decimal(clients_with_transactions) / Decimal(total_clients) * 100
                if total_clients > 0 else Decimal('0.00')
            ),
            'redemption_rate': (
                Decimal(clients_with_redemptions) / Decimal(active_clients) * 100
                if active_clients > 0 else Decimal('0.00')
            )
        }

