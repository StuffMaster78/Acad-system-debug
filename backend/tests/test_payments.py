"""
Comprehensive tests for payment endpoints and services.
Tests critical payment flows including wallet payments, discounts, and refunds.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from tests.factories import (
    ClientUserFactory, OrderFactory, WebsiteFactory,
    ClientWalletFactory
)
from orders.models import Order
from order_payments_management.models import OrderPayment
from order_payments_management.services.payment_service import OrderPaymentService
try:
    from wallet.exceptions import InsufficientWalletBalance
except ImportError:
    # Fallback if wallet app structure is different
    class InsufficientWalletBalance(Exception):
        """Raised when wallet balance is insufficient."""
        pass


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestPaymentCreation:
    """Tests for payment creation."""
    
    def test_create_payment_requires_authentication(self, api_client, order):
        """Test creating payment requires authentication."""
        url = f'/api/v1/order-payments/orders/{order.id}/initiate'
        data = {
            'payment_method': 'wallet'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_payment_success(self, authenticated_client, client_user, order, client_wallet):
        """Test successful payment creation."""
        # Ensure wallet has sufficient balance
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        url = f'/api/v1/order-payments/orders/{order.id}/initiate'
        data = {
            'payment_method': 'wallet'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'payment' in response.data
        assert 'payment_identifier' in response.data
        assert response.data['message'] == 'Payment processed successfully.'
    
    def test_create_payment_insufficient_balance(self, authenticated_client, client_user, order, client_wallet):
        """Test payment creation fails with insufficient wallet balance."""
        # Set wallet balance to less than order total
        client_wallet.balance = Decimal('10.00')
        client_wallet.save()
        
        # Ensure order total is higher
        order.total_price = Decimal('100.00')
        order.save()
        
        url = f'/api/v1/order-payments/orders/{order.id}/initiate'
        data = {
            'payment_method': 'wallet'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_create_payment_with_discount(self, authenticated_client, client_user, order, client_wallet, discount):
        """Test payment creation with discount code."""
        # Ensure wallet has sufficient balance
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        url = f'/api/v1/order-payments/orders/{order.id}/initiate'
        data = {
            'payment_method': 'wallet',
            'discount_code': discount.code
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'payment' in response.data
        # Verify discount was applied
        payment = OrderPayment.objects.get(order=order)
        assert payment.discount_amount > 0


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestWalletPayment:
    """Tests for wallet payment processing."""
    
    def test_pay_with_wallet_success(self, authenticated_client, client_user, order, client_wallet):
        """Test successful wallet payment."""
        # Set sufficient wallet balance
        initial_balance = Decimal('1000.00')
        client_wallet.balance = initial_balance
        client_wallet.save()
        
        order_total = order.total_price
        
        url = f'/api/v1/orders/orders/{order.id}/pay/wallet/'
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify wallet balance was deducted
        client_wallet.refresh_from_db()
        expected_balance = initial_balance - order_total
        assert client_wallet.balance == expected_balance
        
        # Verify order is marked as paid
        order.refresh_from_db()
        assert order.is_paid is True
        
        # Verify payment record was created
        payment = OrderPayment.objects.filter(order=order).first()
        assert payment is not None
        assert payment.status == 'completed'
        assert payment.payment_method == 'wallet'
    
    def test_pay_with_wallet_insufficient_balance(self, authenticated_client, client_user, order, client_wallet):
        """Test wallet payment fails with insufficient balance."""
        # Set insufficient wallet balance
        client_wallet.balance = Decimal('10.00')
        client_wallet.save()
        
        order.total_price = Decimal('100.00')
        order.save()
        
        url = f'/api/v1/orders/orders/{order.id}/pay/wallet/'
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data or 'detail' in response.data
        
        # Verify wallet balance unchanged
        client_wallet.refresh_from_db()
        assert client_wallet.balance == Decimal('10.00')
        
        # Verify order not paid
        order.refresh_from_db()
        assert order.is_paid is False
    
    def test_pay_with_wallet_already_paid(self, authenticated_client, client_user, order, client_wallet):
        """Test wallet payment fails if order already paid."""
        # Mark order as paid
        order.is_paid = True
        order.save()
        
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        url = f'/api/v1/orders/orders/{order.id}/pay/wallet/'
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already paid' in response.data.get('detail', '').lower()
    
    def test_pay_with_wallet_unauthorized(self, authenticated_client, writer_user, order):
        """Test wallet payment requires order ownership or staff privileges."""
        url = f'/api/v1/orders/orders/{order.id}/pay/wallet/'
        response = authenticated_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestPaymentList:
    """Tests for payment listing endpoints."""
    
    def test_list_payments_requires_authentication(self, api_client):
        """Test listing payments requires authentication."""
        url = '/api/v1/order-payments/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_own_payments(self, authenticated_client, client_user, order, client_wallet):
        """Test client can list their own payments."""
        # Create a payment
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        OrderPaymentService.process_wallet_payment(payment)
        
        url = '/api/v1/order-payments/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get('results', [])) >= 1
        assert any(p['id'] == payment.id for p in response.data.get('results', []))
    
    def test_list_payments_filter_by_status(self, authenticated_client, client_user, order, client_wallet):
        """Test filtering payments by status."""
        # Create payments with different statuses
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        payment1 = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet'
        )
        OrderPaymentService.process_wallet_payment(payment1)
        
        # Create pending payment
        order2 = OrderFactory(client=client_user, website=order.website)
        payment2 = OrderPaymentService.create_payment(
            order=order2,
            client=client_user,
            payment_method='manual',
            amount=order2.total_price
        )
        
        url = '/api/v1/order-payments/?status=completed'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', [])
        assert all(p['status'] == 'completed' for p in results)
        assert any(p['id'] == payment1.id for p in results)
        assert not any(p['id'] == payment2.id for p in results)


@pytest.mark.unit
@pytest.mark.payment
class TestPaymentService:
    """Unit tests for OrderPaymentService."""
    
    def test_create_payment_calculates_total(self, order, client_user):
        """Test payment creation calculates total correctly."""
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        
        assert payment.amount == order.total_price
        assert payment.status == 'pending'
        assert payment.payment_method == 'wallet'
        assert payment.order == order
        assert payment.client == client_user
    
    def test_process_wallet_payment_deducts_balance(self, order, client_user, client_wallet):
        """Test wallet payment processing deducts balance correctly."""
        initial_balance = Decimal('1000.00')
        client_wallet.balance = initial_balance
        client_wallet.save()
        
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        
        processed_payment = OrderPaymentService.process_wallet_payment(payment)
        
        assert processed_payment.status == 'completed'
        client_wallet.refresh_from_db()
        assert client_wallet.balance == initial_balance - order.total_price
    
    def test_process_wallet_payment_insufficient_balance_raises_error(self, order, client_user, client_wallet):
        """Test wallet payment raises error on insufficient balance."""
        client_wallet.balance = Decimal('10.00')
        client_wallet.save()
        
        order.total_price = Decimal('100.00')
        order.save()
        
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        
        with pytest.raises(InsufficientWalletBalance):
            OrderPaymentService.process_wallet_payment(payment)
        
        # Verify payment still pending
        payment.refresh_from_db()
        assert payment.status == 'pending'
        
        # Verify balance unchanged
        client_wallet.refresh_from_db()
        assert client_wallet.balance == Decimal('10.00')

