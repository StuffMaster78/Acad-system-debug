"""
Comprehensive tests for HoldOrderService.

Tests cover:
- Putting orders on hold
- Resuming orders
- Status validation
- Notifications
- Edge cases
"""
import pytest
from unittest.mock import patch, MagicMock

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.order_hold_service import HoldOrderService


@pytest.mark.django_db
class TestHoldOrderService:
    """Test HoldOrderService functionality."""
    
    def test_put_on_hold_from_pending(self, order, admin_user):
        """Test putting order on hold from pending status."""
        order.status = OrderStatus.PENDING.value
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with patch('orders.services.order_hold_service.NotificationHelper') as mock_notify:
            result = service.put_on_hold()
        
        result.refresh_from_db()
        assert result.status == OrderStatus.ON_HOLD.value
    
    def test_put_on_hold_from_in_progress(self, order, admin_user):
        """Test putting order on hold from in_progress status."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with patch('orders.services.order_hold_service.NotificationHelper'):
            result = service.put_on_hold()
        
        result.refresh_from_db()
        assert result.status == OrderStatus.ON_HOLD.value
    
    def test_put_on_hold_invalid_status(self, order, admin_user):
        """Test putting order on hold from invalid status raises error."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with pytest.raises(ValueError) as exc:
            service.put_on_hold()
        
        assert "cannot be put on hold" in str(exc.value).lower()
    
    def test_put_on_hold_sends_notifications(self, order, admin_user, client_user, writer_user):
        """Test putting on hold sends notifications to client and writer."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.client = client_user
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        mock_notify = MagicMock()
        with patch('orders.services.order_hold_service.NotificationHelper', mock_notify):
            service.put_on_hold()
        
        # Should send notifications
        assert mock_notify.send_notification.call_count >= 1
    
    def test_resume_from_on_hold(self, order, admin_user):
        """Test resuming order from on_hold status."""
        order.status = OrderStatus.ON_HOLD.value
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with patch('orders.services.order_hold_service.NotificationHelper'):
            result = service.resume()
        
        result.refresh_from_db()
        assert result.status == OrderStatus.IN_PROGRESS.value
    
    def test_resume_invalid_status(self, order, admin_user):
        """Test resuming order from invalid status raises error."""
        order.status = OrderStatus.PENDING.value
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with pytest.raises(ValueError) as exc:
            service.resume()
        
        assert "only on_hold orders" in str(exc.value).lower()
    
    def test_resume_sends_notifications(self, order, admin_user, client_user, writer_user):
        """Test resuming sends notifications to client and writer."""
        order.status = OrderStatus.ON_HOLD.value
        order.client = client_user
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        mock_notify = MagicMock()
        with patch('orders.services.order_hold_service.NotificationHelper', mock_notify):
            service.resume()
        
        # Should send notifications
        assert mock_notify.send_notification.call_count >= 1
    
    def test_put_on_hold_no_client_no_error(self, order, admin_user):
        """Test putting on hold without client doesn't error."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.client = None
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with patch('orders.services.order_hold_service.NotificationHelper'):
            result = service.put_on_hold()
        
        result.refresh_from_db()
        assert result.status == OrderStatus.ON_HOLD.value
    
    def test_resume_no_writer_no_error(self, order, admin_user, client_user):
        """Test resuming without writer doesn't error."""
        order.status = OrderStatus.ON_HOLD.value
        order.client = client_user
        order.assigned_writer = None
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        with patch('orders.services.order_hold_service.NotificationHelper'):
            result = service.resume()
        
        result.refresh_from_db()
        assert result.status == OrderStatus.IN_PROGRESS.value


@pytest.mark.django_db
class TestHoldOrderServiceEdgeCases:
    """Test edge cases for hold service."""
    
    def test_put_on_hold_notification_failure_doesnt_block(self, order, admin_user, client_user):
        """Test notification failure doesn't prevent hold."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.client = client_user
        order.is_paid = True
        order.save()
        
        service = HoldOrderService(order, admin_user)
        
        # Mock notification to raise exception
        with patch('orders.services.order_hold_service.NotificationHelper.send_notification', side_effect=Exception("Notification failed")):
            result = service.put_on_hold()
        
        # Should still succeed
        result.refresh_from_db()
        assert result.status == OrderStatus.ON_HOLD.value

