"""
Integration tests for complete order lifecycle.
Tests the full flow from order creation to completion.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from order_payments_management.models import OrderPayment
from order_payments_management.services.payment_service import OrderPaymentService
from client_wallet.models import ClientWallet


@pytest.mark.integration
@pytest.mark.e2e
class TestOrderLifecycle:
    """Tests for complete order lifecycle."""
    
    def test_order_creation_to_payment(self, client_user, website, authenticated_client):
        """Test order creation and payment flow."""
        # Create order
        order_data = {
            'topic': 'Test Order Topic',
            'number_of_pages': 5,
            'total_price': Decimal('100.00'),
            'client_deadline': (timezone.now() + timedelta(days=7)).isoformat(),
            'order_instructions': 'Test instructions',
            'status': 'draft'
        }
        
        url = '/api/v1/orders/'
        response = authenticated_client.post(url, order_data, format='json')
        
        assert response.status_code in [201, 200]
        order_id = response.data.get('id')
        assert order_id is not None
        
        # Verify order was created
        order = Order.objects.get(id=order_id)
        assert order.client == client_user
        assert order.status == 'draft'
    
    def test_order_payment_flow(self, client_user, website, order, client_wallet, authenticated_client):
        """Test complete payment flow for an order."""
        # Ensure wallet has sufficient balance
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        # Update order to pending status
        order.status = 'pending'
        order.is_paid = False
        order.save()
        
        # Create payment
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        
        assert payment is not None
        assert payment.order == order
        assert payment.amount == order.total_price
        
        # Process wallet payment
        processed_payment = OrderPaymentService.process_wallet_payment(payment)
        
        assert processed_payment.status == 'completed'
        assert processed_payment.confirmed_at is not None
        
        # Verify wallet balance was deducted
        client_wallet.refresh_from_db()
        assert client_wallet.balance < Decimal('1000.00')
        
        # Verify order is marked as paid
        order.refresh_from_db()
        assert order.is_paid is True


@pytest.mark.integration
@pytest.mark.e2e
class TestOrderStatusTransitions:
    """Tests for order status transitions."""
    
    def test_order_status_draft_to_pending(self, order):
        """Test order status transition from draft to pending."""
        assert order.status == 'draft'
        
        order.status = 'pending'
        order.save()
        
        order.refresh_from_db()
        assert order.status == 'pending'
    
    def test_order_status_pending_to_in_progress(self, order, writer_user):
        """Test order status transition from pending to in_progress."""
        order.status = 'pending'
        order.assigned_writer = writer_user
        order.save()
        
        order.status = 'in_progress'
        order.save()
        
        order.refresh_from_db()
        assert order.status == 'in_progress'
        assert order.assigned_writer == writer_user
    
    def test_order_status_in_progress_to_completed(self, order, writer_user):
        """Test order status transition from in_progress to completed."""
        order.status = 'in_progress'
        order.assigned_writer = writer_user
        order.save()
        
        order.status = 'completed'
        order.save()
        
        order.refresh_from_db()
        assert order.status == 'completed'


@pytest.mark.integration
@pytest.mark.e2e
class TestOrderPaymentIntegration:
    """Tests for order payment integration."""
    
    def test_order_payment_with_discount(self, client_user, website, order, client_wallet, discount):
        """Test order payment with discount applied."""
        # Ensure wallet has sufficient balance
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        # Create payment with discount
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price,
            discount_code=discount.code
        )
        
        assert payment is not None
        assert payment.discount_amount > 0
        assert payment.discounted_amount < payment.amount
    
    def test_order_payment_insufficient_balance(self, client_user, website, order, client_wallet):
        """Test order payment fails with insufficient wallet balance."""
        # Set wallet balance to less than order total
        client_wallet.balance = Decimal('10.00')
        client_wallet.save()
        
        order.total_price = Decimal('100.00')
        order.save()
        
        # Create payment
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        
        # Try to process payment - should raise error
        with pytest.raises(ValueError, match="Insufficient wallet balance"):
            OrderPaymentService.process_wallet_payment(payment)

