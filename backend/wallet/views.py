from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from websites.models.websites import Website
from wallet.services.wallet_transaction_service import WalletTransactionService
from .models import WithdrawalRequest
from .serializers import (
    WalletTopUpSerializer,
    WalletWithdrawSerializer,
    WithdrawalRequestSerializer
)


class WalletViewSet(viewsets.ViewSet):
    """
    ViewSet for managing Wallet operations.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_website(self, request):
        website = getattr(request.user, "website", None)
        if website:
            return website

        website_id = request.query_params.get("website") or request.data.get("website")
        if website_id:
            return Website.objects.filter(id=website_id).first()

        return Website.objects.filter(is_active=True).first()

    def _wallet_payload(self, wallet):
        return {
            "id": wallet.id,
            "user": str(wallet.owner_user),
            "website": wallet.website_id,
            "wallet_type": wallet.wallet_type,
            "currency": wallet.currency,
            "available_balance": wallet.available_balance,
            "pending_balance": wallet.pending_balance,
            "total_credited": wallet.total_credited,
            "total_debited": wallet.total_debited,
            "last_activity_at": wallet.last_activity_at,
            "updated_at": wallet.updated_at,
        }

    def list(self, request):
        """
        List wallet details for the authenticated user.
        """
        website = self._get_website(request)
        if not website:
            return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
        wallet = WalletTransactionService.get_wallet(request.user, website)
        return Response(self._wallet_payload(wallet))

    @action(detail=False, methods=['post'], url_path='top-up')
    def top_up(self, request):
        """
        Top up the authenticated user's wallet.
        """
        serializer = WalletTopUpSerializer(data=request.data)
        if serializer.is_valid():
            website = self._get_website(request)
            if not website:
                return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

            amount = serializer.validated_data['amount']
            entry = WalletTransactionService.credit(
                user=request.user,
                website=website,
                amount=amount,
                description=serializer.validated_data.get('description', 'Wallet Top-Up'),
                source="wallet_top_up",
                transaction_type="top-up",
                created_by=request.user,
            )
            return Response(
                {
                    "message": "Wallet successfully topped up!",
                    "entry_id": entry.id,
                    "wallet_balance": entry.balance_after,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='withdraw')
    def withdraw(self, request):
        """
        Handle withdrawal requests for writers.
        """
        serializer = WalletWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            website = self._get_website(request)
            if not website:
                return Response({"error": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

            amount = serializer.validated_data['amount']
            wallet = WalletTransactionService.get_wallet(request.user, website)
            if wallet.available_balance < amount:
                return Response({"error": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)

            entry = WalletTransactionService.debit(
                user=request.user,
                website=website,
                amount=amount,
                description=serializer.validated_data.get('description', 'Wallet Withdrawal'),
                source="wallet_withdrawal",
                transaction_type="withdrawal",
                created_by=request.user,
            )
            return Response(
                {
                    "message": "Withdrawal request successfully processed!",
                    "entry_id": entry.id,
                    "wallet_balance": entry.balance_after,
                },
                status=status.HTTP_200_OK,
            )
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
