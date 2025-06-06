from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (LoyaltyTier, LoyaltyTransaction,
                     Milestone, ClientBadge,
                     LoyaltyPointsConversionConfig
)
from .serializers import (LoyaltyTierSerializer, LoyaltyTransactionSerializer,
                          MilestoneSerializer, ClientBadgeSerializer,
                          LoyaltyPointsConversionConfigSerializer
)
from .permissions import IsAdminOrReadOnly, IsClient, IsOwnerOrAdmin


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