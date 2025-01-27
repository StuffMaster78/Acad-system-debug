from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ClientProfile, LoyaltyTransaction
from .serializers import ClientProfileSerializer, LoyaltyTransactionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from orders.models import Order
from client_management.models import LoyaltyPoint, LoyaltyPointHistory
from client_management.serializers import LoyaltyPointSerializer, LoyaltyPointHistorySerializer
from wallet.models import Wallet, WalletTransaction

class ClientProfileDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a client's profile details.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ClientProfileSerializer

    def get_queryset(self):
        return ClientProfile.objects.filter(client=self.request.user)


class LoyaltyTransactionListView(generics.ListAPIView):
    """
    API endpoint to list loyalty transactions for a client.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LoyaltyTransactionSerializer

    def get_queryset(self):
        return LoyaltyTransaction.objects.filter(client__client=self.request.user)
    


class RequestAccountDeletionView(APIView):
    """
    API endpoint for clients to request account deletion.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Ensure only clients can request account deletion
        if user.role != "client":
            return Response({"error": "Only clients can request account deletion."}, status=status.HTTP_403_FORBIDDEN)

        if user.is_deletion_requested:
            return Response(
                {"error": "Account deletion has already been requested."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Freeze account and log deletion request
        user.freeze_account()
        return Response(
            {
                "message": "Account deletion request submitted. Your account has been frozen.",
                "deletion_date": user.deletion_date,
            },
            status=status.HTTP_200_OK,
        )


class ReinstateAccountView(APIView):
    """
    API endpoint for clients to reinstate their frozen accounts.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.is_deletion_requested:
            return Response(
                {"error": "Your account deletion has not been requested."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.deletion_date and user.deletion_date < now():
            return Response(
                {"error": "Your account is already scheduled for deletion."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reinstate account
        user.reinstate_account()
        return Response(
            {"message": "Your account has been reinstated successfully."},
            status=status.HTTP_200_OK,
        )


class LoyaltyPointView(APIView):
    """
    API to get the current loyalty points for the client.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        loyalty_point = LoyaltyPoint.objects.filter(client=request.user).first()
        if loyalty_point:
            serializer = LoyaltyPointSerializer(loyalty_point)
            return Response(serializer.data)
        return Response({"points": 0})


class LoyaltyPointHistoryView(APIView):
    """
    API to get loyalty point history for the client.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = LoyaltyPointHistory.objects.filter(client=request.user).order_by('-timestamp')
        serializer = LoyaltyPointHistorySerializer(history, many=True)
        return Response(serializer.data)

class RedeemPointsToWalletView(APIView):
    """
    API for clients to redeem loyalty points for wallet credits.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = request.user
        points_to_redeem = request.data.get("points", 0)

        try:
            # Get loyalty points and config
            loyalty_point = LoyaltyPoint.objects.get(client=client)
            config = LoyaltyPointConfig.objects.first()
            if not config:
                return Response({"error": "Loyalty point configuration is not set."}, status=500)

            # Validate points redemption
            if points_to_redeem > loyalty_point.points:
                return Response({"error": "Insufficient points."}, status=400)
            if points_to_redeem < config.minimum_points_redeem:
                return Response(
                    {"error": f"Minimum {config.minimum_points_redeem} points required to redeem."},
                    status=400,
                )

            # Calculate cash equivalent
            cash_value = points_to_redeem / config.points_per_dollar

            # Update wallet
            wallet, _ = Wallet.objects.get_or_create(client=client)
            wallet.balance += cash_value
            wallet.save()

            # Deduct points and log history
            loyalty_point.points -= points_to_redeem
            loyalty_point.save()
            LoyaltyPointHistory.objects.create(
                client=client,
                points_change=-points_to_redeem,
                reason=f"Redeemed {points_to_redeem} points for ${cash_value:.2f}",
            )

            # Log wallet transaction
            WalletTransaction.objects.create(
                client=client,
                amount=cash_value,
                transaction_type="credit",
                reason=f"Redeemed {points_to_redeem} loyalty points",
            )

            return Response(
                {"message": f"Successfully redeemed {points_to_redeem} points for ${cash_value:.2f}. Wallet balance updated."},
                status=200,
            )

        except LoyaltyPoint.DoesNotExist:
            return Response({"error": "No loyalty points found for this client."}, status=404)