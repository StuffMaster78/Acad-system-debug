from decimal import Decimal
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from .models import Wallet, WalletTransaction, WithdrawalRequest
from .serializers import (
    WalletSerializer,
    WalletTransactionSerializer,
    WalletTopUpSerializer,
    WalletWithdrawSerializer,
    WithdrawalRequestSerializer
)


class WalletViewSet(viewsets.ViewSet):
    """
    ViewSet for managing Wallet operations.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        List wallet details for the authenticated user.
        """
        wallet = Wallet.objects.filter(user=request.user).first()
        if not wallet:
            return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='top-up')
    def top_up(self, request):
        """
        Top up the authenticated user's wallet.
        """
        serializer = WalletTopUpSerializer(data=request.data)
        if serializer.is_valid():
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

            amount = serializer.validated_data['amount']
            wallet.balance += amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="top-up",
                amount=amount,
                description=serializer.validated_data.get('description', 'Wallet Top-Up'),
                website=wallet.website
            )
            return Response({"message": "Wallet successfully topped up!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='withdraw')
    def withdraw(self, request):
        """
        Handle withdrawal requests for writers.
        """
        serializer = WalletWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            wallet = Wallet.objects.filter(user=request.user).first()
            if not wallet:
                return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

            amount = serializer.validated_data['amount']
            if wallet.balance < amount:
                return Response({"error": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)

            wallet.balance -= amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="withdrawal",
                amount=amount,
                description=serializer.validated_data.get('description', 'Wallet Withdrawal'),
                website=wallet.website
            )
            return Response({"message": "Withdrawal request successfully processed!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing withdrawal requests.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WithdrawalRequestSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return WithdrawalRequest.objects.all()
        return WithdrawalRequest.objects.filter(wallet__user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='approve')
    def approve_request(self, request, pk=None):
        """
        Admin approves a withdrawal request.
        """
        withdrawal_request = WithdrawalRequest.objects.filter(pk=pk, status='pending').first()
        if not withdrawal_request:
            return Response({"error": "Request not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

        try:
            withdrawal_request.approve(request.user)
            return Response({"message": "Withdrawal request approved."}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='reject')
    def reject_request(self, request, pk=None):
        """
        Admin rejects a withdrawal request.
        """
        withdrawal_request = WithdrawalRequest.objects.filter(pk=pk, status='pending').first()
        if not withdrawal_request:
            return Response({"error": "Request not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

        withdrawal_request.reject(request.user)
        return Response({"message": "Withdrawal request rejected."}, status=status.HTTP_200_OK)