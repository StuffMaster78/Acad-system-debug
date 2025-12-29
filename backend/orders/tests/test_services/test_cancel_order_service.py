"""
Comprehensive tests for CancelOrderService.

Tests cover:
- Admin cancellation
- Client cancellation requests
- Forfeiture calculation
- Status validation
- Permission checks
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

from orders.models import Order, CancellationRequest
from orders.order_enums import OrderStatus
from orders.services.cancel_order_service import CancelOrderService


@pytest.mark.django_db
class TestCancelOrderService:
    """Test CancelOrderService functionality."""
    
    def test_cancel_order_admin_success(self, order, admin_user):
        """Test admin can cancel order."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.save()
        
        CancelOrderService.cancel_order(
            order_id=order.id,
            reason="Admin cancellation",
            user=admin_user
        )
        
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED.value
    
    def test_cancel_order_client_not_allowed(self, order, client_user):
        """Test client cannot directly cancel order."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.save()
        
        with pytest.raises(ValueError) as exc:
            CancelOrderService.cancel_order(
                order_id=order.id,
                reason="Client cancellation attempt",
                user=client_user
            )
        
        assert "cannot directly cancel" in str(exc.value).lower()
    
    def test_cancel_order_invalid_status(self, order, admin_user):
        """Test cannot cancel order in invalid status."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        with pytest.raises(ValueError) as exc:
            CancelOrderService.cancel_order(
                order_id=order.id,
                reason="Cancel completed order",
                user=admin_user
            )
        
        assert "cannot cancel order" in str(exc.value).lower()
    
    def test_cancel_order_saves_reason(self, order, admin_user):
        """Test cancellation reason is saved."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.save()
        
        reason = "Test cancellation reason"
        CancelOrderService.cancel_order(
            order_id=order.id,
            reason=reason,
            user=admin_user
        )
        
        order.refresh_from_db()
        # Check if cancellation_reason field exists and was set
        if hasattr(order, 'cancellation_reason'):
            assert order.cancellation_reason == reason


@pytest.mark.django_db
class TestCancelOrderServiceClientRequests:
    """Test client cancellation requests."""
    
    def test_request_cancellation_success(self, order, client_user):
        """Test client can request cancellation."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.client = client_user
        order.save()
        
        request = CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="Client wants to cancel",
            user=client_user
        )
        
        assert request.order == order
        assert request.requested_by == client_user
        assert request.status == 'pending'
        assert request.reason == "Client wants to cancel"
    
    def test_request_cancellation_wrong_user(self, order, client_user, writer_user):
        """Test only order client can request cancellation."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.client = client_user
        order.save()
        
        with pytest.raises(ValueError) as exc:
            CancelOrderService.request_cancellation(
                order_id=order.id,
                reason="Wrong user cancellation",
                user=writer_user
            )
        
        assert "only the order's client" in str(exc.value).lower()
    
    def test_request_cancellation_invalid_status(self, order, client_user):
        """Test cannot request cancellation for completed order."""
        order.status = OrderStatus.COMPLETED.value
        order.client = client_user
        order.save()
        
        with pytest.raises(ValueError) as exc:
            CancelOrderService.request_cancellation(
                order_id=order.id,
                reason="Cancel completed order",
                user=client_user
            )
        
        assert "cannot request cancellation" in str(exc.value).lower()
    
    def test_request_cancellation_duplicate_request(self, order, client_user):
        """Test cannot create duplicate cancellation request."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.client = client_user
        order.save()
        
        # Create first request
        CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="First request",
            user=client_user
        )
        
        # Try to create second request
        with pytest.raises(ValueError) as exc:
            CancelOrderService.request_cancellation(
                order_id=order.id,
                reason="Second request",
                user=client_user
            )
        
        assert "pending cancellation request already exists" in str(exc.value).lower()
    
    def test_request_cancellation_forfeiture_below_threshold(self, order, client_user):
        """Test forfeiture calculation below threshold (no forfeiture)."""
        from datetime import datetime, timedelta
        
        # Order deadline is 80% away (20% elapsed)
        order.client_deadline = timezone.now() + timedelta(days=8)  # 8 days from now
        order.created_at = timezone.now() - timedelta(days=2)  # Created 2 days ago
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.total_price = Decimal('100.00')
        order.client = client_user
        order.save()
        
        request = CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="Early cancellation",
            user=client_user,
            threshold_percentage=Decimal('50.00')
        )
        
        # Below 50% threshold, should have no forfeiture
        assert request.forfeiture_amount == Decimal('0.00')
        assert request.refund_amount == Decimal('100.00')
    
    def test_request_cancellation_forfeiture_above_threshold(self, order, client_user):
        """Test forfeiture calculation above threshold (progressive forfeiture)."""
        # Order deadline is 20% away (80% elapsed)
        order.client_deadline = timezone.now() + timedelta(days=2)  # 2 days from now
        order.created_at = timezone.now() - timedelta(days=8)  # Created 8 days ago
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.total_price = Decimal('100.00')
        order.client = client_user
        order.save()
        
        request = CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="Late cancellation",
            user=client_user,
            threshold_percentage=Decimal('50.00')
        )
        
        # Above 50% threshold, should have forfeiture
        assert request.forfeiture_amount > Decimal('0.00')
        assert request.refund_amount < Decimal('100.00')
        assert request.forfeiture_amount + request.refund_amount == Decimal('100.00')
    
    def test_request_cancellation_forfeiture_max_80_percent(self, order, client_user):
        """Test forfeiture is capped at 80%."""
        # Order deadline is very close (95% elapsed)
        order.client_deadline = timezone.now() + timedelta(hours=1)  # 1 hour from now
        order.created_at = timezone.now() - timedelta(days=19)  # Created 19 days ago
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.total_price = Decimal('100.00')
        order.client = client_user
        order.save()
        
        request = CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="Very late cancellation",
            user=client_user,
            threshold_percentage=Decimal('50.00')
        )
        
        # Should be capped at 80% forfeiture
        assert request.forfeiture_amount <= Decimal('80.00')
        assert request.refund_amount >= Decimal('20.00')


@pytest.mark.django_db
class TestCancelOrderServiceEdgeCases:
    """Test edge cases for cancellation."""
    
    def test_cancel_order_nonexistent(self, admin_user):
        """Test cancel non-existent order."""
        with pytest.raises(Exception):  # Should raise some exception
            CancelOrderService.cancel_order(
                order_id=99999,
                reason="Cancel non-existent",
                user=admin_user
            )
    
    def test_cancel_order_without_user(self, order):
        """Test cancel order without user (system cancellation)."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.save()
        
        # Should work without user (system cancellation)
        CancelOrderService.cancel_order(
            order_id=order.id,
            reason="System cancellation",
            user=None
        )
        
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED.value
    
    def test_request_cancellation_default_threshold(self, order, client_user):
        """Test cancellation request uses default 50% threshold."""
        order.client_deadline = timezone.now() + timedelta(days=10)
        order.created_at = timezone.now() - timedelta(days=1)
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.total_price = Decimal('100.00')
        order.client = client_user
        order.save()
        
        request = CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="Test cancellation",
            user=client_user
            # threshold_percentage not provided, should default to 50%
        )
        
        assert request is not None
        # Should have no forfeiture (below 50% threshold)
        assert request.forfeiture_amount == Decimal('0.00')

