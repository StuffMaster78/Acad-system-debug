from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Q, F, OrderBy
from django.core.exceptions import ValidationError
from .models import ClientWallet, ClientWalletTransaction, LoyaltyTransaction, LoyaltyPointsConversionConfig
from referrals.models import ReferralBonusConfig
from .serializers import ClientWalletSerializer, ClientWalletTransactionSerializer, LoyaltyTransactionSerializer, ReferralBonusSerializer, ReferralStatsSerializer
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.utils import timezone
from admin_management.permissions import IsAdmin


class WalletPagination(PageNumberPagination):
    """Pagination for wallet listings"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

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
        Get all transactions for the client's wallet with pagination.
        """
        wallet = self.get_object()
        transactions = ClientWalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        
        # Paginate transactions
        paginator = WalletPagination()
        page = paginator.paginate_queryset(transactions, request)
        
        if page is not None:
            serializer = ClientWalletTransactionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Fallback: return all transactions
        serializer = ClientWalletTransactionSerializer(transactions, many=True)
        return Response({
            'results': serializer.data,
            'count': transactions.count(),
            'next': None,
            'previous': None
        })

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
        Convert loyalty points to wallet balance (by wallet ID).
        """
        wallet = self.get_object()
        try:
            converted_amount = wallet.convert_loyalty_points_to_wallet()
            return Response({"detail": f"Loyalty points converted to ${converted_amount}"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def convert_my_loyalty_points(self, request):
        """
        Convert loyalty points to wallet balance (for authenticated user's wallet).
        """
        try:
            wallet = ClientWallet.objects.get(user=request.user)
            converted_amount = wallet.convert_loyalty_points_to_wallet()
            wallet.refresh_from_db()
            serializer = ClientWalletSerializer(wallet)
            return Response({
                "detail": f"Loyalty points converted to ${converted_amount}",
                "wallet": serializer.data
            }, status=status.HTTP_200_OK)
        except ClientWallet.DoesNotExist:
            return Response(
                {"detail": "Wallet not found. Please contact support."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        """
        Get the authenticated client's wallet with transactions.
        """
        try:
            wallet = ClientWallet.objects.select_related('user', 'website').get(user=request.user)
            serializer = ClientWalletSerializer(wallet)
            
            # Get recent transactions
            transactions = ClientWalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:50]
            transaction_serializer = ClientWalletTransactionSerializer(transactions, many=True)
            
            return Response({
                'wallet': serializer.data,
                'transactions': transaction_serializer.data
            })
        except ClientWallet.DoesNotExist:
            return Response(
                {"detail": "Wallet not found. Please contact support."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def top_up(self, request):
        """
        Top up the client's wallet (client-initiated payment).
        """
        try:
            wallet = ClientWallet.objects.select_for_update().get(user=request.user)
        except ClientWallet.DoesNotExist:
            return Response(
                {"detail": "Wallet not found. Please contact support."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        amount = request.data.get('amount')
        description = request.data.get('description', 'Wallet top-up')
        
        if not amount:
            return Response(
                {"detail": "Amount is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response(
                    {"detail": "Amount must be greater than 0."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid amount format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Credit wallet with top-up transaction type
        wallet.credit_wallet(amount, description or 'Wallet top-up')
        
        # Update transaction type to 'top-up' (client payment)
        last_transaction = ClientWalletTransaction.objects.filter(
            wallet=wallet
        ).order_by('-created_at').first()
        if last_transaction:
            last_transaction.transaction_type = 'top-up'
            last_transaction.save()
        
        # Refresh wallet
        wallet.refresh_from_db()
        serializer = ClientWalletSerializer(wallet)
        
        return Response({
            'detail': f'Wallet topped up successfully! ${amount:,.2f} added.',
            'wallet': serializer.data
        }, status=status.HTTP_200_OK)

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

        # Calculate referral balance from pending referral bonus transactions
        from django.db.models import Sum
        referral_transactions = wallet.transactions.filter(transaction_type='referral_bonus', amount__gt=0)
        referral_balance = referral_transactions.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        if referral_balance <= 0:
            return Response({"detail": "No referral bonus to claim."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate bonus to claim
        bonus_to_claim = (referral_balance * Decimal(bonus)) / 100

        wallet.credit_wallet(bonus_to_claim, reason="Referral bonus claimed")
        # Note: referral_balance is computed from transactions, so we don't need to set it to 0
        # The referral bonus transactions remain in the history

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


# Admin Wallet Management ViewSet
class AdminWalletManagementViewSet(viewsets.ViewSet):
    """Admin-only wallet management with totals and adjustments"""
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = WalletPagination
    
    def list(self, request):
        """List all client wallets with filtering, pagination, and summary totals"""
        queryset = ClientWallet.objects.select_related('user', 'website').all()
        
        # Filter by website if admin is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Apply filters
        website_id = request.query_params.get('website')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        # Amount filters
        min_balance = request.query_params.get('min_balance')
        if min_balance:
            try:
                queryset = queryset.filter(balance__gte=Decimal(min_balance))
            except (ValueError, TypeError):
                pass
        
        max_balance = request.query_params.get('max_balance')
        if max_balance:
            try:
                queryset = queryset.filter(balance__lte=Decimal(max_balance))
            except (ValueError, TypeError):
                pass
        
        # Search filter (email, username, name)
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__phone_number__icontains=search)
            )
        
        # Sorting
        ordering = request.query_params.get('ordering', '-balance')
        if ordering:
            # Validate ordering field
            allowed_fields = ['balance', '-balance', 'last_updated', '-last_updated', 'loyalty_points', '-loyalty_points']
            if ordering in allowed_fields:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by('-balance')
        else:
            queryset = queryset.order_by('-balance')
        
        # Calculate totals BEFORE pagination
        totals = queryset.aggregate(
            total_balance=Sum('balance'),
            total_wallets=Count('id'),
            total_loyalty_points=Sum('loyalty_points')
        )
        
        # Group by website - include all websites even if they have no wallets
        from websites.models import Website
        
        # Get all websites (for superadmin) or admin's website
        if request.user.role == 'superadmin':
            all_websites = Website.objects.filter(is_deleted=False)
        else:
            admin_website = getattr(request.user, 'website', None)
            all_websites = Website.objects.filter(id=admin_website.id, is_deleted=False) if admin_website else Website.objects.none()
        
        # Get wallet totals per website
        wallet_totals = queryset.values('website__id', 'website__name', 'website__domain').annotate(
            total_balance=Sum('balance'),
            wallet_count=Count('id')
        )
        
        # Create a map of website totals
        totals_map = {item['website__id']: item for item in wallet_totals}
        
        # Build website_totals including all websites
        website_totals = []
        for website in all_websites:
            if website.id in totals_map:
                website_totals.append(totals_map[website.id])
            else:
                # Website with no wallets
                website_totals.append({
                    'website__id': website.id,
                    'website__name': website.name,
                    'website__domain': website.domain,
                    'total_balance': Decimal('0.00'),
                    'wallet_count': 0
                })
        
        # Sort by total balance descending
        website_totals = sorted(website_totals, key=lambda x: float(x['total_balance'] or 0), reverse=True)
        
        # Paginate wallets
        paginator = WalletPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = ClientWalletSerializer(page, many=True)
            # Create custom paginated response with summary
            response = paginator.get_paginated_response(serializer.data)
            # Add summary to response data
            response.data['summary'] = {
                'total_balance': float(totals['total_balance'] or Decimal('0.00')),
                'total_wallets': totals['total_wallets'] or 0,
                'total_loyalty_points': totals['total_loyalty_points'] or 0,
                'website_totals': list(website_totals),
            }
            # Rename results to wallets for consistency
            if 'results' in response.data:
                response.data['wallets'] = response.data.pop('results')
            return response
        
        # Fallback if pagination is not used
        serializer = ClientWalletSerializer(queryset, many=True)
        return Response({
            'wallets': serializer.data,
            'summary': {
                'total_balance': float(totals['total_balance'] or Decimal('0.00')),
                'total_wallets': totals['total_wallets'] or 0,
                'total_loyalty_points': totals['total_loyalty_points'] or 0,
                'website_totals': list(website_totals),
            }
        })
    
    def retrieve(self, request, pk=None):
        """Get a specific wallet with paginated transactions"""
        wallet = get_object_or_404(ClientWallet.objects.select_related('user', 'website'), pk=pk)
        
        # Check website permission
        if request.user.role != 'superadmin':
            admin_website = getattr(request.user, 'website', None)
            if admin_website and wallet.website != admin_website:
                return Response(
                    {"detail": "You don't have permission to view this wallet."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = ClientWalletSerializer(wallet)
        
        # Get transactions with pagination
        transactions = ClientWalletTransaction.objects.filter(wallet=wallet).select_related('wallet__user', 'wallet__website').order_by('-created_at')
        
        # Paginate transactions
        paginator = WalletPagination()
        page = paginator.paginate_queryset(transactions, request)
        
        if page is not None:
            transaction_serializer = ClientWalletTransactionSerializer(page, many=True)
            return paginator.get_paginated_response({
                'wallet': serializer.data,
                'transactions': transaction_serializer.data
            })
        
        # Fallback: return last 50 transactions
        transactions = transactions[:50]
        transaction_serializer = ClientWalletTransactionSerializer(transactions, many=True)
        
        return Response({
            'wallet': serializer.data,
            'transactions': transaction_serializer.data,
            'count': transactions.count(),
            'next': None,
            'previous': None
        })
    
    @action(detail=True, methods=['post'])
    def adjust(self, request, pk=None):
        """Admin adjustment: credit or debit wallet"""
        wallet = get_object_or_404(ClientWallet.objects.select_related('user', 'website'), pk=pk)
        
        # Check website permission
        if request.user.role != 'superadmin':
            admin_website = getattr(request.user, 'website', None)
            if admin_website and wallet.website != admin_website:
                return Response(
                    {"detail": "You don't have permission to adjust this wallet."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        amount = request.data.get('amount')
        reason = request.data.get('reason', '')
        transaction_type = request.data.get('transaction_type', 'adjustment')
        
        if not amount:
            return Response(
                {"detail": "Amount is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Invalid amount."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount == 0:
            return Response(
                {"detail": "Amount cannot be zero."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if amount > 0:
                # Credit
                wallet.credit_wallet(amount, reason)
                # Update transaction type if different
                if transaction_type != 'top-up':
                    last_transaction = ClientWalletTransaction.objects.filter(
                        wallet=wallet
                    ).order_by('-created_at').first()
                    if last_transaction:
                        last_transaction.transaction_type = transaction_type
                        last_transaction.save()
                
                message = f'Successfully credited ${amount:,.2f} to {wallet.user.get_full_name() or wallet.user.username}\'s wallet.'
            else:
                # Debit (make amount positive)
                debit_amount = abs(amount)
                wallet.debit_wallet(debit_amount, reason)
                # Update transaction type if different
                if transaction_type != 'payment':
                    last_transaction = ClientWalletTransaction.objects.filter(
                        wallet=wallet
                    ).order_by('-created_at').first()
                    if last_transaction:
                        last_transaction.transaction_type = transaction_type
                        last_transaction.save()
                
                message = f'Successfully debited ${debit_amount:,.2f} from {wallet.user.get_full_name() or wallet.user.username}\'s wallet.'
            
            # Refresh wallet
            wallet.refresh_from_db()
            serializer = ClientWalletSerializer(wallet)
            
            return Response({
                'detail': message,
                'wallet': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )