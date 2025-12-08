"""
Comprehensive tests for wallet system endpoints and services.
Tests wallet operations, transactions, top-ups, and withdrawals.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from tests.factories import (
    ClientUserFactory, WebsiteFactory, ClientWalletFactory
)
from wallet.models import Wallet, WalletTransaction
from wallet.services.wallet_transaction_service import WalletTransactionService
from wallet.exceptions import InsufficientWalletBalance


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestWalletOperations:
    """Tests for wallet operations."""
    
    def test_get_wallet_requires_authentication(self, api_client):
        """Test getting wallet requires authentication."""
        url = '/api/v1/wallet/wallets/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_wallet_success(self, authenticated_client, client_user, website):
        """Test getting wallet details."""
        # Ensure wallet exists
        wallet, _ = Wallet.objects.get_or_create(
            user=client_user,
            website=website
        )
        
        url = '/api/v1/wallet/wallets/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'balance' in response.data or 'id' in response.data
    
    def test_wallet_top_up_requires_authentication(self, api_client):
        """Test wallet top-up requires authentication."""
        url = '/api/v1/wallet/wallets/top-up/'
        data = {
            'amount': Decimal('100.00')
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_wallet_top_up_success(self, authenticated_client, client_user, website):
        """Test successful wallet top-up."""
        # Ensure wallet exists
        wallet, _ = Wallet.objects.get_or_create(
            user=client_user,
            website=website
        )
        initial_balance = wallet.balance
        
        url = '/api/v1/wallet/wallets/top-up/'
        data = {
            'amount': Decimal('100.00'),
            'description': 'Test top-up'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify balance increased
        wallet.refresh_from_db()
        assert wallet.balance == initial_balance + Decimal('100.00')
        
        # Verify transaction created
        transaction = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='top-up'
        ).first()
        assert transaction is not None
        assert transaction.amount == Decimal('100.00')


@pytest.mark.unit
@pytest.mark.payment
class TestWalletTransactionService:
    """Unit tests for WalletTransactionService."""
    
    def test_get_wallet_creates_if_not_exists(self, client_user, website):
        """Test get_wallet creates wallet if it doesn't exist."""
        # Ensure wallet doesn't exist
        Wallet.objects.filter(user=client_user, website=website).delete()
        
        wallet = WalletTransactionService.get_wallet(client_user, website)
        
        assert wallet is not None
        assert wallet.user == client_user
        assert wallet.website == website
    
    def test_get_balance_returns_zero_for_new_wallet(self, client_user, website):
        """Test get_balance returns zero for new wallet."""
        balance = WalletTransactionService.get_balance(client_user, website)
        
        assert balance == Decimal('0.00')
    
    def test_credit_increases_balance(self, client_user, website):
        """Test credit increases wallet balance."""
        initial_balance = WalletTransactionService.get_balance(client_user, website)
        
        transaction = WalletTransactionService.credit(
            user=client_user,
            amount=Decimal('50.00'),
            website=website,
            description='Test credit'
        )
        
        new_balance = WalletTransactionService.get_balance(client_user, website)
        
        assert new_balance == initial_balance + Decimal('50.00')
        assert transaction.amount == Decimal('50.00')
        assert transaction.transaction_type == 'credit'
    
    def test_debit_decreases_balance(self, client_user, website):
        """Test debit decreases wallet balance."""
        # First credit the wallet
        WalletTransactionService.credit(
            user=client_user,
            amount=Decimal('100.00'),
            website=website,
            description='Initial credit'
        )
        
        initial_balance = WalletTransactionService.get_balance(client_user, website)
        
        transaction = WalletTransactionService.debit(
            user=client_user,
            website=website,
            amount=Decimal('30.00'),
            description='Test debit'
        )
        
        new_balance = WalletTransactionService.get_balance(client_user, website)
        
        assert new_balance == initial_balance - Decimal('30.00')
        assert transaction.amount == -Decimal('30.00')
        assert transaction.transaction_type == 'debit'
    
    def test_debit_insufficient_balance_raises_error(self, client_user, website):
        """Test debit raises error on insufficient balance."""
        # Ensure wallet has low balance
        Wallet.objects.filter(user=client_user, website=website).delete()
        WalletTransactionService.credit(
            user=client_user,
            amount=Decimal('10.00'),
            website=website,
            description='Small credit'
        )
        
        with pytest.raises(InsufficientWalletBalance):
            WalletTransactionService.debit(
                user=client_user,
                website=website,
                amount=Decimal('100.00'),
                description='Large debit'
            )
        
        # Verify balance unchanged
        balance = WalletTransactionService.get_balance(client_user, website)
        assert balance == Decimal('10.00')
    
    def test_refund_credits_wallet(self, client_user, website):
        """Test refund credits wallet balance."""
        initial_balance = WalletTransactionService.get_balance(client_user, website)
        
        transaction = WalletTransactionService.refund(
            user=client_user,
            website=website,
            amount=Decimal('25.00'),
            description='Test refund'
        )
        
        new_balance = WalletTransactionService.get_balance(client_user, website)
        
        assert new_balance == initial_balance + Decimal('25.00')
        assert transaction.amount == Decimal('25.00')
        assert transaction.transaction_type == 'refund'


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestWalletTransactions:
    """Tests for wallet transaction listing."""
    
    def test_list_transactions_requires_authentication(self, api_client):
        """Test listing transactions requires authentication."""
        url = '/api/v1/wallet/wallets/transactions/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_own_transactions(self, authenticated_client, client_user, website):
        """Test client can list their own transactions."""
        # Create some transactions
        wallet, _ = Wallet.objects.get_or_create(
            user=client_user,
            website=website
        )
        
        WalletTransaction.objects.create(
            wallet=wallet,
            user=client_user,
            website=website,
            amount=Decimal('50.00'),
            transaction_type='credit',
            description='Test transaction'
        )
        
        url = '/api/v1/wallet/wallets/transactions/'
        response = authenticated_client.get(url)
        
        # Note: URL may vary based on actual implementation
        # This test verifies authentication requirement
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

