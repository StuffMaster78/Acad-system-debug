"""
Comprehensive tests for MarkOrderPaidService.

Tests cover:
- Marking order as paid
- Payment validation
- Status transitions
- Notifications
- Error handling
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.mark_order_as_paid_service import MarkOrderPaidService
from order_payments_management.models import OrderPayment
from decimal import Decimal


@pytest.mark.django_db
class TestMarkOrderPaidService:
    """Test MarkOrderPaidService functionality."""
    
    def test_mark_paid_success(self, order, client_user):
        """Test successfully marking order as paid."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        # Create completed payment
        OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=order.total_price or Decimal('100.00'),
            status='completed',
            payment_method='wallet'
        )
        
        service = MarkOrderPaidService()
        
        with patch('orders.services.mark_order_as_paid_service.NotificationHelper') as mock_notify:
            result = service.mark_paid(order.id)
        
        result.refresh_from_db()
        assert result.is_paid is True
        assert result.status == OrderStatus.IN_PROGRESS.value
    
    def test_mark_paid_from_pending(self, order, client_user):
        """Test marking paid from pending status."""
        order.status = OrderStatus.PENDING.value
        order.is_paid = False
        order.save()
        
        OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=order.total_price or Decimal('100.00'),
            status='completed',
            payment_method='wallet'
        )
        
        service = MarkOrderPaidService()
        
        with patch('orders.services.mark_order_as_paid_service.NotificationHelper'):
            result = service.mark_paid(order.id)
        
        result.refresh_from_db()
        assert result.is_paid is True
        assert result.status == OrderStatus.IN_PROGRESS.value
    
    def test_mark_paid_no_payment(self, order):
        """Test marking paid without payment raises error."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        service = MarkOrderPaidService()
        
        with pytest.raises(ValidationError) as exc:
            service.mark_paid(order.id)
        
        assert "no completed payment" in str(exc.value).lower()
    
    def test_mark_paid_invalid_status(self, order, client_user):
        """Test marking paid from invalid status raises error."""
        order.status = OrderStatus.COMPLETED.value
        order.is_paid = False
        order.save()
        
        OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=order.total_price or Decimal('100.00'),
            status='completed',
            payment_method='wallet'
        )
        
        service = MarkOrderPaidService()
        
        with pytest.raises(ValueError) as exc:
            service.mark_paid(order.id)
        
        assert "cannot be marked paid" in str(exc.value).lower()
    
    def test_mark_paid_sends_notification(self, order, client_user):
        """Test marking paid sends notification."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        payment = OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=Decimal('100.00'),
            discounted_amount=Decimal('90.00'),
            status='completed',
            payment_method='wallet'
        )
        
        service = MarkOrderPaidService()
        
        mock_notify = MagicMock()
        with patch('orders.services.mark_order_as_paid_service.NotificationHelper', mock_notify):
            service.mark_paid(order.id)
        
        mock_notify.notify_order_paid.assert_called_once()
        call_kwargs = mock_notify.notify_order_paid.call_args[1]
        assert call_kwargs['order'] == order
        assert call_kwargs['payment_amount'] == Decimal('90.00')
        assert call_kwargs['payment_method'] == 'wallet'
    
    def test_mark_paid_with_succeeded_status(self, order, client_user):
        """Test marking paid accepts 'succeeded' payment status."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=order.total_price or Decimal('100.00'),
            status='succeeded',  # Alternative status
            payment_method='stripe'
        )
        
        service = MarkOrderPaidService()
        
        with patch('orders.services.mark_order_as_paid_service.NotificationHelper'):
            result = service.mark_paid(order.id)
        
        result.refresh_from_db()
        assert result.is_paid is True


@pytest.mark.django_db
class TestMarkOrderPaidServiceEdgeCases:
    """Test edge cases for marking order as paid."""
    
    def test_mark_paid_pending_payment_not_accepted(self, order, client_user):
        """Test pending payment is not accepted."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=order.total_price or Decimal('100.00'),
            status='pending',  # Not completed
            payment_method='stripe'
        )
        
        service = MarkOrderPaidService()
        
        with pytest.raises(ValidationError) as exc:
            service.mark_paid(order.id)
        
        assert "no completed payment" in str(exc.value).lower()
    
    def test_mark_paid_multiple_payments_uses_latest(self, order, client_user):
        """Test with multiple payments, uses latest completed."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        # Create old payment
        old_payment = OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=Decimal('50.00'),
            status='completed',
            payment_method='wallet'
        )
        
        # Create newer payment
        new_payment = OrderPayment.objects.create(
            order=order,
            client=client_user,
            website=order.website,
            amount=Decimal('100.00'),
            status='completed',
            payment_method='wallet'
        )
        
        service = MarkOrderPaidService()
        
        mock_notify = MagicMock()
        with patch('orders.services.mark_order_as_paid_service.NotificationHelper', mock_notify):
            service.mark_paid(order.id)
        
        # Should use the latest payment
        call_kwargs = mock_notify.notify_order_paid.call_args[1]
        assert call_kwargs['payment_amount'] == Decimal('100.00')

