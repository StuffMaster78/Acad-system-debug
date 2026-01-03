"""
Service for managing client badge awards and analytics.
"""
from django.utils.timezone import now
from loyalty_management.models import ClientBadge
from client_management.models import ClientProfile
from orders.models import Order
from order_payments_management.models import OrderPayment
from django.db.models import Count, Sum, Q
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ClientBadgeService:
    """Service for managing client badge awards."""
    
    @staticmethod
    def award_badge(client: ClientProfile, badge_name: str, description: str = "", website=None):
        """
        Award a badge to a client.
        :param client: The client to award the badge to.
        :param badge_name: The name of the badge.
        :param description: Optional description for the award.
        :param website: Optional website context.
        :return: The ClientBadge instance if awarded, None if already awarded.
        """
        website = website or client.website
        
        if ClientBadge.objects.filter(
            client=client, badge_name=badge_name, website=website
        ).exists():
            return None  # Already awarded
        
        client_badge = ClientBadge.objects.create(
            client=client,
            badge_name=badge_name,
            description=description,
            website=website
        )
        
        return client_badge
    
    @staticmethod
    def evaluate_and_award_badges(client: ClientProfile):
        """
        Evaluate and auto-award badges based on client metrics.
        """
        awarded = []
        website = client.website
        
        # Calculate client metrics
        metrics = ClientBadgeService._calculate_metrics(client)
        
        # Top Spender: $5000+ total spent
        if metrics['total_spent'] >= Decimal('5000'):
            result = ClientBadgeService.award_badge(
                client, "Top Spender", 
                f"Spent over ${metrics['total_spent']:,.2f} on orders",
                website
            )
            if result:
                awarded.append("Top Spender")
        
        # Loyal Customer: 50+ orders
        if metrics['total_orders'] >= 50:
            result = ClientBadgeService.award_badge(
                client, "Loyal Customer",
                f"Placed {metrics['total_orders']} orders",
                website
            )
            if result:
                awarded.append("Loyal Customer")
        
        # Early Adopter: First 100 clients
        if metrics['registration_rank'] <= 100:
            result = ClientBadgeService.award_badge(
                client, "Early Adopter",
                "One of the first 100 clients",
                website
            )
            if result:
                awarded.append("Early Adopter")
        
        # High Roller: Single order over $1000
        if metrics['max_order_value'] >= Decimal('1000'):
            result = ClientBadgeService.award_badge(
                client, "High Roller",
                f"Placed an order worth ${metrics['max_order_value']:,.2f}",
                website
            )
            if result:
                awarded.append("High Roller")
        
        # Consistent Client: 10+ orders in last 3 months
        if metrics['recent_orders'] >= 10:
            result = ClientBadgeService.award_badge(
                client, "Consistent Client",
                f"{metrics['recent_orders']} orders in the last 3 months",
                website
            )
            if result:
                awarded.append("Consistent Client")
        
        # Perfect Client: 20+ orders, 0 disputes
        if metrics['total_orders'] >= 20 and metrics['dispute_count'] == 0:
            result = ClientBadgeService.award_badge(
                client, "Perfect Client",
                f"{metrics['total_orders']} orders with zero disputes",
                website
            )
            if result:
                awarded.append("Perfect Client")
        
        return awarded
    
    @staticmethod
    def _calculate_metrics(client: ClientProfile):
        """Calculate client metrics for badge evaluation."""
        from django.utils import timezone
        from datetime import timedelta
        
        three_months_ago = timezone.now() - timedelta(days=90)
        
        orders = Order.objects.filter(client=client.user)
        payments = OrderPayment.objects.filter(order__client=client.user, status='completed')
        
        total_spent = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_orders = orders.count()
        recent_orders = orders.filter(created_at__gte=three_months_ago).count()
        max_order_value = payments.aggregate(max=Sum('amount'))['max'] or Decimal('0')
        dispute_count = orders.filter(status='disputed').count()
        
        # Calculate registration rank (simplified - would need proper ranking)
        registration_rank = ClientProfile.objects.filter(
            website=client.website,
            user__date_joined__lt=client.user.date_joined
        ).count() + 1
        
        return {
            'total_spent': total_spent,
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'max_order_value': max_order_value,
            'dispute_count': dispute_count,
            'registration_rank': registration_rank
        }
    
    @staticmethod
    def get_client_badges(client: ClientProfile):
        """Get all badges for a client."""
        return ClientBadge.objects.filter(
            client=client
        ).order_by('-awarded_at')
    
    @staticmethod
    def get_badge_statistics(client: ClientProfile):
        """Get badge statistics for a client."""
        badges = ClientBadgeService.get_client_badges(client)
        
        return {
            'total_badges': badges.count(),
            'badges': [
                {
                    'name': badge.badge_name,
                    'description': badge.description,
                    'awarded_at': badge.awarded_at
                }
                for badge in badges
            ]
        }

