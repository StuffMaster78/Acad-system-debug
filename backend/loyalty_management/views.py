from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (
    LoyaltyTier, LoyaltyTransaction,
    Milestone, ClientBadge,
    LoyaltyPointsConversionConfig,
    RedemptionCategory, RedemptionItem, RedemptionRequest,
    LoyaltyAnalytics, DashboardWidget
)
from .serializers import (
    LoyaltyTierSerializer, LoyaltyTransactionSerializer,
    MilestoneSerializer, ClientBadgeSerializer,
    LoyaltyPointsConversionConfigSerializer,
    LoyaltyConversionSerializer, LoyaltySummarySerializer,
    AdminLoyaltyAwardSerializer, AdminLoyaltyDeductSerializer,
    AdminLoyaltyForceConvertSerializer, AdminLoyaltyTransferSerializer,
    RedemptionCategorySerializer, RedemptionItemSerializer, RedemptionRequestSerializer,
    CreateRedemptionRequestSerializer, ApproveRedemptionSerializer, RejectRedemptionSerializer,
    LoyaltyAnalyticsSerializer, DashboardWidgetSerializer,
    PointsTrendSerializer, TopRedemptionItemSerializer, TierDistributionSerializer,
    EngagementStatsSerializer
)
from .permissions import IsAdminOrReadOnly, IsClient, IsOwnerOrAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from client_management.models import ClientProfile
from loyalty_management.services.loyalty_conversion_service import LoyaltyConversionService
from loyalty_management.services.redemption_service import RedemptionService
from loyalty_management.services.analytics_service import LoyaltyAnalyticsService
from websites.utils import get_current_website
from rest_framework.generics import ListAPIView
from wallet.services.wallet_transaction_service import WalletTransactionService



class LoyaltyTierViewSet(ModelViewSet):
    """
    ViewSet for managing loyalty tiers.
    Admin users have full access; other users have read-only access.
    """
    queryset = LoyaltyTier.objects.all()
    serializer_class = LoyaltyTierSerializer
    permission_classes = [IsAdminOrReadOnly]


class LoyaltyTransactionViewSet(ModelViewSet):
    """
    ViewSet for managing loyalty transactions.
    Clients can only access their own transactions; admins can access all.
    """
    queryset = LoyaltyTransaction.objects.all()
    serializer_class = LoyaltyTransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Restrict queryset to the logged-in client's transactions unless the user is an admin.
        """
        if self.request.user.is_staff:
            return LoyaltyTransaction.objects.all()
        return LoyaltyTransaction.objects.filter(client__user=self.request.user)


class MilestoneViewSet(ModelViewSet):
    """
    ViewSet for managing milestones.
    Admin users have full access; other users have read-only access.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAdminOrReadOnly]


class ClientBadgeViewSet(ModelViewSet):
    """
    ViewSet for managing client badges.
    Clients can view their own badges; admins can access all badges.
    """
    queryset = ClientBadge.objects.all()
    serializer_class = ClientBadgeSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """
        Restrict queryset to the logged-in client's badges unless the user is an admin.
        """
        if self.request.user.is_staff:
            return ClientBadge.objects.all()
        return ClientBadge.objects.filter(client__user=self.request.user)
    
class LoyaltyPointsConversionConfigViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing the LoyaltyPointsConversionConfig model.
    Allows admins to view and update loyalty points conversion settings.
    """
    queryset = LoyaltyPointsConversionConfig.objects.all()
    serializer_class = LoyaltyPointsConversionConfigSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Filter by website if needed (you can extend this logic).
        """
        return LoyaltyPointsConversionConfig.objects.filter(website=self.request.website)
    

class AdminForceConversionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, client_id):
        points = int(request.data.get("points", 0))
        website = get_current_website(request)

        client = ClientProfile.objects.get(id=client_id)
        try:
            amount = LoyaltyConversionService.convert_points_to_wallet(
                client=client,
                website=website,
                points=points
            )
            return Response({
                "success": True,
                "converted_amount": str(amount),
                "converted_points": points
            })
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        


class LoyaltySummaryView(APIView):
    def get(self, request):
        client = request.user.client_profile
        website = client.website

        config = LoyaltyPointsConversionConfig.objects.filter(website=website, active=True).first()
        data = {
            "loyalty_points": client.loyalty_points,
            "wallet_balance": WalletTransactionService.get_balance(request.user, website),  # Add website parameter
            "tier": client.tier.name if client.tier else "None",
            "conversion_rate": config.conversion_rate if config else "0.00"
        }
        return Response(LoyaltySummarySerializer(data).data)
    

class LoyaltyConvertView(APIView):
    def post(self, request):
        serializer = LoyaltyConversionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        points = serializer.validated_data['points']
        client = request.user.client_profile
        website = client.website

        amount = LoyaltyConversionService.convert_points_to_wallet(client, website, points)

        return Response({"converted": points, "amount": str(amount)}, status=status.HTTP_200_OK)
    

class LoyaltyTransactionListView(ListAPIView):
    serializer_class = LoyaltyTransactionSerializer

    def get_queryset(self):
        # LoyaltyTransaction model uses 'timestamp' not 'created_at'
        return LoyaltyTransaction.objects.filter(client=self.request.user.client_profile).order_by("-timestamp")
    
class AdminLoyaltyAwardView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminLoyaltyAwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = serializer.validated_data['client_id']
        points = serializer.validated_data['points']
        reason = serializer.validated_data.get('reason', 'Manual Award')

        client = ClientProfile.objects.get(id=client_id)
        transaction = LoyaltyTransaction.objects.create(
            client=client,
            points=points,
            transaction_type=LoyaltyTransaction.TransactionType.AWARD,
            reason=reason
        )

        return Response(LoyaltyTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
    
class AdminLoyaltyDeductView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminLoyaltyDeductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = serializer.validated_data['client_id']
        points = serializer.validated_data['points']
        reason = serializer.validated_data.get('reason', 'Manual Deduction')

        client = ClientProfile.objects.get(id=client_id)
        transaction = LoyaltyTransaction.objects.create(
            client=client,
            points=-points,
            transaction_type=LoyaltyTransaction.TransactionType.DEDUCTION,
            reason=reason
        )

        return Response(LoyaltyTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED) 
    
class AdminLoyaltyTransferView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminLoyaltyTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from_client_id = serializer.validated_data['from_client_id']
        to_client_id = serializer.validated_data['to_client_id']
        points = serializer.validated_data['points']
        reason = serializer.validated_data.get('reason', 'Manual Transfer')

        from_client = ClientProfile.objects.get(id=from_client_id)
        to_client = ClientProfile.objects.get(id=to_client_id)

        if from_client.loyalty_points < points:
            return Response({"detail": _("Insufficient loyalty points.")}, status=status.HTTP_400_BAD_REQUEST)

        # Create deduction transaction for the sender
        LoyaltyTransaction.objects.create(
            client=from_client,
            points=-points,
            transaction_type=LoyaltyTransaction.TransactionType.TRANSFER_OUT,
            reason=reason
        )

        # Create award transaction for the receiver
        transaction = LoyaltyTransaction.objects.create(
            client=to_client,
            points=points,
            transaction_type=LoyaltyTransaction.TransactionType.TRANSFER_IN,
            reason=reason
        )

        return Response(LoyaltyTransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
    
class AdminLoyaltyConversionConfigView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        website = get_current_website(request)
        if not website:
            return Response({"detail": _("Website not found.")}, status=status.HTTP_400_BAD_REQUEST)
        
        config = LoyaltyPointsConversionConfig.objects.filter(website=website).first()
        if not config:
            return Response({"detail": _("No conversion configuration found.")}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LoyaltyPointsConversionConfigSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        website = get_current_website(request)
        if not website:
            return Response({"detail": _("Website not found.")}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = LoyaltyPointsConversionConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        config, created = LoyaltyPointsConversionConfig.objects.update_or_create(
            website=website,
            defaults=serializer.validated_data
        )

        return Response(LoyaltyPointsConversionConfigSerializer(config).data, status=status.HTTP_200_OK)
    
class AdminLoyaltyAwardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = AdminLoyaltyAwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        LoyaltyConversionService.award_points(
            client_profile=data["client_id"],
            website=data["website_id"],
            points=data["points"],
            reason=data["reason"],
        )

        return Response({"detail": "Points awarded successfully."}, status=status.HTTP_200_OK)


class AdminLoyaltyForceConvertView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = AdminLoyaltyForceConvertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        amount = LoyaltyConversionService.convert_points_to_wallet(
            client=data["client_id"],
            website=data["website_id"],
            points=data["points"]
        )

        return Response(
            {
                "detail": f"{data['points']} points converted to ${amount} wallet balance."
            },
            status=status.HTTP_200_OK
        )


# ============================================================================
# REDEMPTION SYSTEM VIEWSETS
# ============================================================================

class RedemptionCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing redemption categories.
    """
    queryset = RedemptionCategory.objects.all()
    serializer_class = RedemptionCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        """Filter by website if available."""
        queryset = super().get_queryset()
        website = get_current_website(self.request)
        if website:
            queryset = queryset.filter(website=website, is_active=True)
        return queryset


class RedemptionItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing redemption items.
    Clients can view available items; admins have full access.
    """
    queryset = RedemptionItem.objects.all()
    serializer_class = RedemptionItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by website and active status."""
        queryset = super().get_queryset()
        website = get_current_website(self.request)
        if website:
            queryset = queryset.filter(website=website)
        
        # Clients only see active items
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        # Filter by category if provided
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        return queryset.select_related('category', 'min_tier_level')


class RedemptionRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing redemption requests.
    Clients can create and view their own requests; admins can manage all.
    """
    queryset = RedemptionRequest.objects.all()
    serializer_class = RedemptionRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by user role."""
        queryset = super().get_queryset()
        website = get_current_website(self.request)
        if website:
            queryset = queryset.filter(website=website)
        
        # Clients only see their own requests
        if not self.request.user.is_staff:
            try:
                client_profile = self.request.user.client_profile
                queryset = queryset.filter(client=client_profile)
            except:
                queryset = queryset.none()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('item', 'item__category', 'client', 'client__user')
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.action == 'create':
            return CreateRedemptionRequestSerializer
        return RedemptionRequestSerializer
    
    def perform_create(self, serializer):
        """Create redemption request using service."""
        client_profile = self.request.user.client_profile
        item_id = serializer.validated_data['item_id']
        fulfillment_details = serializer.validated_data.get('fulfillment_details', {})
        
        redemption = RedemptionService.create_redemption_request(
            client_profile=client_profile,
            item_id=item_id,
            fulfillment_details=fulfillment_details
        )
        serializer.instance = redemption
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a redemption request."""
        redemption = self.get_object()
        try:
            RedemptionService.approve_redemption(redemption, request.user)
            return Response(
                RedemptionRequestSerializer(redemption).data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a redemption request."""
        redemption = self.get_object()
        serializer = RejectRedemptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            RedemptionService.reject_redemption(
                redemption,
                request.user,
                serializer.validated_data['reason']
            )
            return Response(
                RedemptionRequestSerializer(redemption).data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel a redemption request."""
        redemption = self.get_object()
        
        # Clients can only cancel their own pending requests
        if not request.user.is_staff:
            if redemption.client.user != request.user:
                return Response(
                    {'detail': 'You can only cancel your own redemptions.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            RedemptionService.cancel_redemption(redemption, request.user)
            return Response(
                RedemptionRequestSerializer(redemption).data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# ANALYTICS DASHBOARD VIEWSETS
# ============================================================================

class LoyaltyAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for loyalty analytics (read-only, admin only).
    """
    queryset = LoyaltyAnalytics.objects.all()
    serializer_class = LoyaltyAnalyticsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter by website."""
        queryset = super().get_queryset()
        website = get_current_website(self.request)
        if website:
            queryset = queryset.filter(website=website)
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def calculate(self, request):
        """Calculate analytics for a date range."""
        from datetime import datetime, date
        
        website = get_current_website(request)
        date_from_str = request.data.get('date_from')
        date_to_str = request.data.get('date_to')
        
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else None
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else None
        
        analytics = LoyaltyAnalyticsService.calculate_analytics(
            website=website,
            date_from=date_from,
            date_to=date_to
        )
        
        return Response(
            LoyaltyAnalyticsSerializer(analytics).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def points_trend(self, request):
        """Get points trend over time."""
        website = get_current_website(request)
        days = int(request.query_params.get('days', 30))
        
        trend = LoyaltyAnalyticsService.get_points_trend(website, days)
        serializer = PointsTrendSerializer(trend, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def top_redemptions(self, request):
        """Get top redemption items."""
        website = get_current_website(request)
        limit = int(request.query_params.get('limit', 10))
        
        items = LoyaltyAnalyticsService.get_top_redemption_items(website, limit)
        serializer = TopRedemptionItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def tier_distribution(self, request):
        """Get tier distribution."""
        website = get_current_website(request)
        
        distribution = LoyaltyAnalyticsService.get_tier_distribution(website)
        
        # Convert to list format
        data = [
            {
                'tier_name': tier_name,
                'count': tier_data['count'],
                'threshold': tier_data['threshold'],
                'percentage': tier_data['percentage']
            }
            for tier_name, tier_data in distribution.items()
        ]
        
        serializer = TierDistributionSerializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def engagement_stats(self, request):
        """Get client engagement statistics."""
        website = get_current_website(request)
        days = int(request.query_params.get('days', 30))
        
        stats = LoyaltyAnalyticsService.get_client_engagement_stats(website, days)
        serializer = EngagementStatsSerializer(stats)
        return Response(serializer.data)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing dashboard widgets.
    """
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter by website."""
        queryset = super().get_queryset()
        website = get_current_website(self.request)
        if website:
            queryset = queryset.filter(website=website, is_visible=True)
        return queryset.order_by('position')
