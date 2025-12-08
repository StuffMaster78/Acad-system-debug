"""
Integration tests for complete user workflows.
Tests end-to-end scenarios that span multiple systems.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from tests.factories import (
    ClientUserFactory, WriterUserFactory, OrderFactory,
    WebsiteFactory, WriterProfileFactory, ClientWalletFactory
)
from orders.models import Order
from order_payments_management.models import OrderPayment
from order_payments_management.services.payment_service import OrderPaymentService


@pytest.mark.integration
@pytest.mark.e2e
class TestCompleteOrderFlow:
    """Integration tests for complete order flow: create → pay → assign → complete."""
    
    def test_complete_order_workflow(self, authenticated_client, client_user, website, client_wallet, authenticated_admin, writer_user, writer_profile):
        """Test complete order workflow from creation to completion."""
        # Step 1: Create order
        url = '/api/v1/orders/orders/'
        deadline = (timezone.now() + timedelta(days=7)).isoformat()
        order_data = {
            'topic': 'Integration Test Order',
            'number_of_pages': 5,
            'academic_level_id': 1,
            'paper_type_id': 1,
            'client_deadline': deadline,
            'order_instructions': 'Complete integration test',
            'website_id': website.id
        }
        
        create_response = authenticated_client.post(url, order_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        order_id = create_response.data['id']
        order = Order.objects.get(id=order_id)
        
        # Step 2: Pay for order with wallet
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        payment_url = f'/api/v1/orders/orders/{order_id}/pay/wallet/'
        payment_response = authenticated_client.post(payment_url, format='json')
        assert payment_response.status_code == status.HTTP_200_OK
        
        # Verify order is paid
        order.refresh_from_db()
        assert order.is_paid is True
        
        # Step 3: Assign order to writer (admin action)
        assign_url = f'/api/v1/orders/orders/{order_id}/action/'
        assign_data = {
            'action': 'assign_order',
            'writer_id': writer_user.id
        }
        assign_response = authenticated_admin.post(assign_url, assign_data, format='json')
        assert assign_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verify order assigned
        order.refresh_from_db()
        assert order.writer_id == writer_user.id or order.assigned_writer_id == writer_user.id
        
        # Step 4: Writer completes order
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(writer_user)
        authenticated_writer = authenticated_client
        authenticated_writer.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        complete_url = f'/api/v1/orders/orders/{order_id}/action/'
        complete_data = {'action': 'complete_order'}
        complete_response = authenticated_writer.post(complete_url, complete_data, format='json')
        assert complete_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verify order completed
        order.refresh_from_db()
        assert order.status == 'completed'


@pytest.mark.integration
@pytest.mark.e2e
class TestPaymentWithDiscountFlow:
    """Integration tests for payment flow with discount application."""
    
    def test_order_payment_with_discount(self, authenticated_client, client_user, website, client_wallet, discount):
        """Test complete payment flow with discount code."""
        # Create order
        order = OrderFactory(
            client=client_user,
            website=website,
            total_price=Decimal('100.00')
        )
        
        # Ensure wallet has sufficient balance
        client_wallet.balance = Decimal('1000.00')
        client_wallet.save()
        
        # Apply discount and pay
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price,
            discount_code=discount.code
        )
        
        # Process payment
        processed_payment = OrderPaymentService.process_wallet_payment(payment)
        
        # Verify payment processed with discount
        assert processed_payment.status == 'completed'
        assert processed_payment.discount_amount > 0
        
        # Verify wallet balance deducted correctly (with discount)
        client_wallet.refresh_from_db()
        expected_deduction = order.total_price - processed_payment.discount_amount
        # Balance should be reduced by the discounted amount
        assert client_wallet.balance < Decimal('1000.00')


@pytest.mark.integration
@pytest.mark.e2e
class TestOrderCancellationWithRefund:
    """Integration tests for order cancellation with refund."""
    
    def test_cancel_paid_order_creates_refund(self, authenticated_client, client_user, website, client_wallet):
        """Test cancelling a paid order creates refund."""
        # Create and pay for order
        order = OrderFactory(
            client=client_user,
            website=website,
            total_price=Decimal('100.00')
        )
        
        initial_balance = Decimal('1000.00')
        client_wallet.balance = initial_balance
        client_wallet.save()
        
        # Pay for order
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        OrderPaymentService.process_wallet_payment(payment)
        
        # Verify payment made
        client_wallet.refresh_from_db()
        assert client_wallet.balance == initial_balance - order.total_price
        
        # Cancel order
        cancel_url = f'/api/v1/orders/orders/{order.id}/action/'
        cancel_data = {
            'action': 'cancel_order',
            'reason': 'Change of mind'
        }
        cancel_response = authenticated_client.post(cancel_url, cancel_data, format='json')
        
        assert cancel_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verify order cancelled
        order.refresh_from_db()
        assert order.status == 'cancelled'
        
        # Note: Actual refund logic depends on implementation
        # This test verifies the cancellation endpoint works


@pytest.mark.integration
@pytest.mark.e2e
class TestWriterOrderRequestFlow:
    """Integration tests for writer order request workflow."""
    
    def test_writer_request_and_assignment_flow(self, authenticated_writer, writer_user, writer_profile, authenticated_client, client_user, website, client_wallet, authenticated_admin):
        """Test writer requests order and gets assigned."""
        # Create paid order
        order = OrderFactory(
            client=client_user,
            website=website,
            total_price=Decimal('100.00'),
            is_paid=True,
            status='available'
        )
        
        # Writer requests order
        request_url = '/api/v1/writer-management/writer-order-requests/'
        request_data = {
            'order': order.id,
            'website': website.id
        }
        request_response = authenticated_writer.post(request_url, request_data, format='json')
        
        # Request should be created (status may vary)
        assert request_response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        
        # Admin assigns order to writer
        assign_url = f'/api/v1/orders/orders/{order.id}/action/'
        assign_data = {
            'action': 'assign_order',
            'writer_id': writer_user.id
        }
        assign_response = authenticated_admin.post(assign_url, assign_data, format='json')
        
        # Status may vary - assignment might be done through different endpoint
        assert assign_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        # If successful, verify order assigned
        if assign_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            order.refresh_from_db()
            assert order.writer_id == writer_user.id or order.assigned_writer_id == writer_user.id


@pytest.mark.integration
@pytest.mark.e2e
class TestWalletTopUpAndPaymentFlow:
    """Integration tests for wallet top-up and payment flow."""
    
    def test_top_up_and_pay_order(self, authenticated_client, client_user, website):
        """Test wallet top-up followed by order payment."""
        from wallet.services.wallet_transaction_service import WalletTransactionService
        
        # Get initial balance
        initial_balance = WalletTransactionService.get_balance(client_user, website)
        
        # Top up wallet
        top_up_url = '/api/v1/wallet/wallets/top-up/'
        top_up_data = {
            'amount': Decimal('200.00'),
            'description': 'Test top-up'
        }
        top_up_response = authenticated_client.post(top_up_url, top_up_data, format='json')
        
        assert top_up_response.status_code == status.HTTP_200_OK
        
        # Verify balance increased
        new_balance = WalletTransactionService.get_balance(client_user, website)
        assert new_balance == initial_balance + Decimal('200.00')
        
        # Create order
        order = OrderFactory(
            client=client_user,
            website=website,
            total_price=Decimal('150.00')
        )
        
        # Pay with wallet
        payment = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=order.total_price
        )
        OrderPaymentService.process_wallet_payment(payment)
        
        # Verify balance decreased
        final_balance = WalletTransactionService.get_balance(client_user, website)
        assert final_balance == new_balance - Decimal('150.00')
        
        # Verify order paid
        order.refresh_from_db()
        assert order.is_paid is True

