from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ClientWallet, ClientWalletTransaction, LoyaltyTransaction, ReferralBonusConfig, LoyaltyPointsConversionConfig
from .serializers import ClientWalletSerializer, ClientWalletTransactionSerializer, LoyaltyTransactionSerializer, ReferralBonusSerializer, ReferralStatsSerializer
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.utils import timezone

# ClientWallet ViewSet
class ClientWalletViewSet(viewsets.ModelViewSet):
    queryset = ClientWallet.objects.all()
    serializer_class = ClientWalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get wallet associated with the authenticated user
        return ClientWallet.objects.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get all transactions for the client's wallet.
        """
        wallet = self.get_object()
        transactions = ClientWalletTransaction.objects.filter(wallet=wallet)
        serializer = ClientWalletTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def debit(self, request, pk=None):
        """
        Deduct an amount from the client's wallet.
        """
        wallet = self.get_object()
        amount = request.data.get('amount')
        reason = request.data.get('reason', '')
        
        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        amount = Decimal(amount)

        try:
            wallet.debit_wallet(amount, reason)
            return Response({"detail": "Amount deducted successfully."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def credit(self, request, pk=None):
        """
        Add an amount to the client's wallet.
        """
        wallet = self.get_object()
        amount = request.data.get('amount')
        reason = request.data.get('reason', '')

        if not amount:
            return Response({"detail": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        amount = Decimal(amount)

        wallet.credit_wallet(amount, reason)
        return Response({"detail": "Amount credited successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def convert_loyalty_points(self, request, pk=None):
        """
        Convert loyalty points to wallet balance.
        """
        wallet = self.get_object()
        try:
            converted_amount = wallet.convert_loyalty_points_to_wallet()
            return Response({"detail": f"Loyalty points converted to ${converted_amount}"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Loyalty Transaction ViewSet
class LoyaltyTransactionViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyTransaction.objects.all()
    serializer_class = LoyaltyTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LoyaltyTransaction.objects.filter(client=self.request.user.client_profile)

# Referral Bonus ViewSet
class ReferralBonusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def referral_bonus(self, request):
        """
        Get the client's current referral bonus details.
        """
        wallet = ClientWallet.objects.get(user=request.user)
        serializer = ReferralBonusSerializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def claim_referral_bonus(self, request):
        """
        Claim referral bonus and add to wallet balance.
        """
        wallet = ClientWallet.objects.get(user=request.user)

        # Get the referral bonus config
        referral_bonus_config = ReferralBonusConfig.objects.first()  # assuming one global config
        bonus = referral_bonus_config.bonus_percentage  # Percentage of bonus to be applied

        # Assuming some logic to check if eligible for claiming
        # You can customize this based on the business rules

        if wallet.referral_balance <= 0:
            return Response({"detail": "No referral bonus to claim."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate bonus to claim
        bonus_to_claim = (wallet.referral_balance * Decimal(bonus)) / 100

        wallet.credit_wallet(bonus_to_claim, reason="Referral bonus claimed")
        wallet.referral_balance = 0
        wallet.save()

        return Response({"detail": f"Referral bonus of ${bonus_to_claim} added to your wallet."}, status=status.HTTP_200_OK)

# Referral Stats View
class ReferralStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def referral_stats(self, request):
        """
        Get the stats of referrals for the authenticated user.
        """
        wallet = ClientWallet.objects.get(user=request.user)
        serializer = ReferralStatsSerializer(wallet)
        return Response(serializer.data)