"""
Admin views for loyalty points tracking and management.
Shows how points are awarded, redeemed, and explains the system.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Q, Sum, Avg
from django.utils.timezone import now, timedelta
from loyalty_management.models import LoyaltyTransaction, LoyaltyTier, LoyaltyPointsConversionConfig
from orders.models import Order
from referrals.models import Referral
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination


class LoyaltyTransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for loyalty transactions with explanations."""
    client_username = serializers.CharField(source='client.user.username', read_only=True)
    client_email = serializers.CharField(source='client.user.email', read_only=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    points_awarded = serializers.SerializerMethodField()
    points_redeemed = serializers.SerializerMethodField()
    points_deducted = serializers.SerializerMethodField()
    explanation = serializers.SerializerMethodField()
    
    class Meta:
        model = LoyaltyTransaction
        fields = '__all__'
        read_only_fields = ['timestamp']
    
    def get_points_awarded(self, obj):
        """Return points if transaction is 'add', else 0."""
        return obj.points if obj.transaction_type == 'add' else 0
    
    def get_points_redeemed(self, obj):
        """Return points if transaction is 'redeem', else 0."""
        return obj.points if obj.transaction_type == 'redeem' else 0
    
    def get_points_deducted(self, obj):
        """Return points if transaction is 'deduct', else 0."""
        return obj.points if obj.transaction_type == 'deduct' else 0
    
    def get_explanation(self, obj):
        """Generate human-readable explanation of the transaction."""
        if obj.transaction_type == 'add':
            if 'order' in obj.reason.lower():
                return f"Points awarded for order completion: {obj.reason}"
            elif 'referral' in obj.reason.lower():
                return f"Points awarded for successful referral: {obj.reason}"
            else:
                return f"Points added: {obj.reason}"
        elif obj.transaction_type == 'redeem':
            return f"Points redeemed: {obj.reason}"
        elif obj.transaction_type == 'deduct':
            return f"Points deducted: {obj.reason}"
        return obj.reason or "No explanation provided"


class LoyaltyTrackingPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdminLoyaltyTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin view for tracking all loyalty point transactions.
    Shows detailed information about how points are awarded and redeemed.
    """
    queryset = LoyaltyTransaction.objects.all().select_related(
        'client', 'client__user', 'website', 'redemption_request'
    ).order_by('-timestamp')
    serializer_class = LoyaltyTransactionDetailSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['website', 'transaction_type', 'client']
    search_fields = ['client__user__username', 'client__user__email', 'reason']
    ordering_fields = ['timestamp', 'points']
    ordering = ['-timestamp']
    pagination_class = LoyaltyTrackingPagination
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall loyalty point statistics."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate totals by type
        total_awarded = queryset.filter(transaction_type='add').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_redeemed = queryset.filter(transaction_type='redeem').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_deducted = queryset.filter(transaction_type='deduct').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        # Recent activity
        last_24h = queryset.filter(timestamp__gte=now() - timedelta(days=1))
        last_7d = queryset.filter(timestamp__gte=now() - timedelta(days=7))
        last_30d = queryset.filter(timestamp__gte=now() - timedelta(days=30))
        
        stats = {
            'total_points_awarded': total_awarded,
            'total_points_redeemed': total_redeemed,
            'total_points_deducted': total_deducted,
            'net_points': total_awarded - total_redeemed - total_deducted,
            'total_transactions': queryset.count(),
            'transactions_24h': last_24h.count(),
            'transactions_7d': last_7d.count(),
            'transactions_30d': last_30d.count(),
            'points_awarded_24h': last_24h.filter(transaction_type='add').aggregate(
                total=Sum('points')
            )['total'] or 0,
            'points_awarded_7d': last_7d.filter(transaction_type='add').aggregate(
                total=Sum('points')
            )['total'] or 0,
            'points_awarded_30d': last_30d.filter(transaction_type='add').aggregate(
                total=Sum('points')
            )['total'] or 0,
            'by_transaction_type': queryset.values('transaction_type').annotate(
                count=Count('id'),
                total_points=Sum('points')
            ).values('transaction_type', 'count', 'total_points'),
            'by_website': queryset.values('website__name').annotate(
                count=Count('id'),
                total_points=Sum('points')
            ).values('website__name', 'count', 'total_points'),
            'top_clients': queryset.filter(transaction_type='add').values(
                'client__user__username'
            ).annotate(
                total_points=Sum('points')
            ).order_by('-total_points')[:10],
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def award_sources(self, request):
        """
        Explain how points are awarded.
        Shows breakdown by source (orders, referrals, etc.)
        """
        queryset = self.filter_queryset(
            self.get_queryset().filter(transaction_type='add')
        )
        
        # Analyze reasons to categorize award sources
        sources = {
            'order_completion': 0,
            'referral': 0,
            'manual_award': 0,
            'other': 0,
        }
        
        for transaction in queryset:
            reason_lower = (transaction.reason or '').lower()
            if 'order' in reason_lower or 'completed' in reason_lower:
                sources['order_completion'] += transaction.points
            elif 'referral' in reason_lower:
                sources['referral'] += transaction.points
            elif 'admin' in reason_lower or 'manual' in reason_lower:
                sources['manual_award'] += transaction.points
            else:
                sources['other'] += transaction.points
        
        return Response({
            'award_sources': sources,
            'explanation': {
                'order_completion': 'Points awarded when clients complete orders',
                'referral': 'Points awarded for successful referrals',
                'manual_award': 'Points manually awarded by admins',
                'other': 'Other sources of points'
            }
        })
    
    @action(detail=False, methods=['get'])
    def client_summary(self, request):
        """Get loyalty point summary for a specific client."""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transactions = self.get_queryset().filter(client_id=client_id)
        
        total_earned = transactions.filter(transaction_type='add').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_redeemed = transactions.filter(transaction_type='redeem').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        total_deducted = transactions.filter(transaction_type='deduct').aggregate(
            total=Sum('points')
        )['total'] or 0
        
        return Response({
            'client_id': client_id,
            'total_earned': total_earned,
            'total_redeemed': total_redeemed,
            'total_deducted': total_deducted,
            'current_balance': total_earned - total_redeemed - total_deducted,
            'transaction_count': transactions.count(),
            'recent_transactions': LoyaltyTransactionDetailSerializer(
                transactions[:10],
                many=True
            ).data
        })

