from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (LoyaltyTier, LoyaltyTransaction,
                     Milestone, ClientBadge,
                     LoyaltyPointsConversionConfig
)
from .serializers import (LoyaltyTierSerializer, LoyaltyTransactionSerializer,
                          MilestoneSerializer, ClientBadgeSerializer,
                          LoyaltyPointsConversionConfigSerializer,
                          LoyaltyConversionSerializer, LoyaltySummarySerializer,
                          AdminLoyaltyAwardSerializer, AdminLoyaltyDeductSerializer,
                          AdminLoyaltyForceConvertSerializer, AdminLoyaltyTransferSerializer
)
from .permissions import IsAdminOrReadOnly, IsClient, IsOwnerOrAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.translation import gettext_lazy as _
from client_management.models import ClientProfile
from loyalty_management.services.loyalty_conversion_service import LoyaltyConversionService
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
            "wallet_balance": WalletTransactionService.get_balance(request.user),
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
        return LoyaltyTransaction.objects.filter(client=self.request.user.client_profile).order_by("-created_at")
    
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
        config = LoyaltyPointsConversionConfig.objects.filter(website=get_current_website(request)).first()
        if not config:
            return Response({"detail": _("No conversion configuration found.")}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LoyaltyPointsConversionConfigSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        serializer = LoyaltyPointsConversionConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        config, created = LoyaltyPointsConversionConfig.objects.update_or_create(
            website=get_current_website(request),
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