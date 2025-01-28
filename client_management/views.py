from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from client_management.models import ClientProfile, ProfileUpdateRequest
from loyalty_management.models import LoyaltyTier, LoyaltyTransaction
from client_management.serializers import (
    ClientProfileSerializer,
    ClientActionSerializer,
    ProfileUpdateRequestSerializer
)


from loyalty_management.serializers import  LoyaltyTierSerializer, LoyaltyTransactionSerializer
from core.utils.location import get_geolocation_from_ip
from .permissions import IsAdminOrSuperAdmin, IsSelfOrAdmin
from .pagination import StandardResultsSetPagination
from wallet.models import Wallet
from wallet.serializers import WalletTransactionSerializer
from .tasks import update_loyalty_points


# List and create client profiles (Admin/Superadmin only)
class ClientProfileListView(generics.ListAPIView):
    """
    List all client profiles (Admin/Superadmin only).
    """
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminOrSuperAdmin]


# Retrieve, update, or delete a specific client profile
class ClientProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific client profile.
    Permissions: Admins and self-access for clients.
    """
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsSelfOrAdmin]


# Update client profile (Admins and clients themselves)
class ClientProfileUpdateView(generics.UpdateAPIView):
    """
    Update a client profile, including geolocation updates.
    """
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsSelfOrAdmin]

    def perform_update(self, serializer):
        client_profile = serializer.save()

        # Fetch geolocation from IP
        ip_address = self.request.META.get("REMOTE_ADDR")
        geo_data = get_geolocation_from_ip(ip_address)

        if "error" not in geo_data:
            client_profile.country = geo_data.get("country")
            client_profile.timezone = geo_data.get("timezone")
            client_profile.ip_address = ip_address
            client_profile.location_verified = True
            client_profile.save()
        else:
            print(f"Geolocation error: {geo_data['error']}")


# View wallet balance and transactions for a specific client
class ClientWalletView(views.APIView):
    """
    Retrieve wallet balance and transactions for a specific client.
    Permissions: Admin/Superadmin only.
    """
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, client_id, *args, **kwargs):
        try:
            client = ClientProfile.objects.get(pk=client_id)
            wallet = Wallet.objects.get(user=client.user)
            transactions = wallet.transactions.all()
            wallet_data = {
                "balance": wallet.balance,
                "transactions": WalletTransactionSerializer(transactions, many=True).data,
            }
            return Response(wallet_data, status=status.HTTP_200_OK)
        except ClientProfile.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)


# List and create loyalty tiers (Admin/Superadmin only)
class LoyaltyTierListView(generics.ListCreateAPIView):
    """
    List or create loyalty tiers.
    Permissions: Admin/Superadmin only.
    """
    queryset = LoyaltyTier.objects.all()
    serializer_class = LoyaltyTierSerializer
    permission_classes = [IsAdminOrSuperAdmin]


# Retrieve, update, or delete a specific loyalty tier
class LoyaltyTierDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific loyalty tier.
    Permissions: Admin/Superadmin only.
    """
    queryset = LoyaltyTier.objects.all()
    serializer_class = LoyaltyTierSerializer
    permission_classes = [IsAdminOrSuperAdmin]


# List loyalty transactions for a specific client
class LoyaltyTransactionListView(generics.ListAPIView):
    """
    List all loyalty transactions for a specific client.
    Permissions: Admin/Superadmin only.
    """
    serializer_class = LoyaltyTransactionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        client_id = self.kwargs["client_id"]
        return LoyaltyTransaction.objects.filter(client_id=client_id).order_by("-timestamp")


# Admin actions (suspend, activate, deactivate client accounts)
from rest_framework.response import Response
from .models import ClientAction
from .serializers import ClientActionSerializer

class ClientActionView(views.APIView):
    permission_classes = [IsAdminOrSuperAdmin]
    serializer_class = ClientActionSerializer

    def post(self, request, client_id, *args, **kwargs):
        try:
            client = ClientProfile.objects.get(pk=client_id)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            action = serializer.validated_data.get("action")
            
            # Perform the action and log it
            if action == "suspend":
                client.suspend_account(admin=request.user)
            elif action == "activate":
                client.activate_account(admin=request.user)
            elif action == "deactivate":
                client.deactivate_account(admin=request.user)

            # Create ClientAction record
            ClientAction.objects.create(
                client=client,
                action=action,
                performed_by=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )

            return Response({"message": f"Client account {action}d."}, status=status.HTTP_200_OK)

        except ClientProfile.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

# Create profile update requests
class ProfileUpdateRequestCreateView(generics.CreateAPIView):
    """
    Allow clients to request changes to critical fields.
    Permissions: Authenticated users only.
    """
    queryset = ProfileUpdateRequest.objects.all()
    serializer_class = ProfileUpdateRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        client_profile = ClientProfile.objects.get(user=self.request.user)
        serializer.save(client=client_profile)


# List profile update requests (Admin only)
class ProfileUpdateRequestListView(generics.ListAPIView):
    """
    Allow admins to view all profile update requests.
    Permissions: Admin only.
    """
    queryset = ProfileUpdateRequest.objects.all()
    serializer_class = ProfileUpdateRequestSerializer
    permission_classes = [IsAdminUser]