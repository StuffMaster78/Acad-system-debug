from decimal import Decimal
from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .models import LoyaltyPoint, LoyaltyPointConfig, LoyaltyPointHistory
from wallet.models import Wallet, WalletTransaction

from .models import ClientProfile, LoyaltyTransaction, LoyaltyPoint, LoyaltyPointHistory, LoyaltyPointConfig
from .serializers import (
    ClientProfileSerializer,
    LoyaltyTransactionSerializer,
    LoyaltyPointSerializer,
    LoyaltyPointHistorySerializer,
)
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


class RedeemLoyaltyPointsView(APIView):
    """
    API for clients to redeem loyalty points for wallet credits.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = request.user
        points_to_redeem = request.data.get("points", 0)

        # Validate points input
        try:
            points_to_redeem = int(points_to_redeem)
            if points_to_redeem <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response({"error": "Invalid points value. Must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get loyalty points and config
            loyalty_point = LoyaltyPoint.objects.get(client=client)
            config = LoyaltyPointConfig.objects.first()
            if not config:
                return Response(
                    {"error": "Loyalty point configuration is missing. Please contact support."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Validate points redemption
            if points_to_redeem > loyalty_point.points:
                return Response({"error": "Insufficient points.", "code": "INSUFFICIENT_POINTS"}, status=status.HTTP_400_BAD_REQUEST)
            if points_to_redeem < config.minimum_points_redeem:
                return Response(
                    {
                        "error": f"Minimum {config.minimum_points_redeem} points required to redeem.",
                        "code": "MINIMUM_POINTS_REQUIRED",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Calculate cash equivalent
            cash_value = Decimal(points_to_redeem) / Decimal(config.points_per_dollar)

            # Atomic transaction for wallet and points update
            with transaction.atomic():
                # Update wallet
                wallet, _ = Wallet.objects.get_or_create(user=client)
                wallet.balance += cash_value
                wallet.save()

                # Deduct points
                loyalty_point.points -= points_to_redeem
                loyalty_point.save()

                # Log history
                LoyaltyPointHistory.objects.create(
                    client=client,
                    points_change=-points_to_redeem,
                    reason=f"Redeemed {points_to_redeem} points for ${cash_value:.2f}",
                )

                # Log wallet transaction
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type="credit",
                    amount=cash_value,
                    description=f"Redeemed {points_to_redeem} loyalty points",
                )

            return Response(
                {
                    "message": f"Successfully redeemed {points_to_redeem} points for ${cash_value:.2f}. Wallet balance updated.",
                    "wallet_balance": wallet.balance,
                    "remaining_points": loyalty_point.points,
                },
                status=status.HTTP_200_OK,
            )

        except LoyaltyPoint.DoesNotExist:
            return Response(
                {"error": "No loyalty points found for this client.", "code": "NO_LOYALTY_POINTS"},
                status=status.HTTP_404_NOT_FOUND,
            )