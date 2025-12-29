"""
Comprehensive tests for ReopenOrderService.

Tests cover:
- Reopening cancelled orders
- Reopening archived orders
- Reopening completed orders
- Status validation
- Reopen tracking fields
"""
import pytest
from datetime import datetime
from unittest.mock import patch

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.reopen_order_service import ReopenOrderService


@pytest.mark.django_db
class TestReopenOrderService:
    """Test ReopenOrderService functionality."""
    
    def test_reopen_cancelled_order(self, order):
        """Test reopening cancelled order."""
        order.status = OrderStatus.CANCELLED.value
        order.save()
        
        service = ReopenOrderService()
        result = service.reopen_order(order.id, "Client wants to continue")
        
        result.refresh_from_db()
        assert result.status == OrderStatus.UNPAID.value
        assert result.reopened_from == OrderStatus.CANCELLED.value
        assert result.reopen_reason == "Client wants to continue"
        assert result.reopened_at is not None
    
    def test_reopen_archived_order(self, order):
        """Test reopening archived order."""
        order.status = OrderStatus.ARCHIVED.value
        order.save()
        
        service = ReopenOrderService()
        result = service.reopen_order(order.id, "Need to make changes")
        
        result.refresh_from_db()
        assert result.status == OrderStatus.IN_PROGRESS.value
        assert result.reopened_from == OrderStatus.ARCHIVED.value
        assert result.reopen_reason == "Need to make changes"
    
    def test_reopen_completed_order(self, order):
        """Test reopening completed order."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = ReopenOrderService()
        result = service.reopen_order(order.id, "Client requested changes")
        
        result.refresh_from_db()
        assert result.status == OrderStatus.IN_PROGRESS.value
        assert result.reopened_from == OrderStatus.COMPLETED.value
    
    def test_reopen_order_invalid_status(self, order):
        """Test reopening order from invalid status raises error."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        service = ReopenOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.reopen_order(order.id, "Test")
        
        assert "cannot be reopened" in str(exc.value).lower()
    
    def test_reopen_order_not_found(self):
        """Test reopening non-existent order raises error."""
        service = ReopenOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.reopen_order(99999, "Test")
        
        assert "not found" in str(exc.value).lower()
    
    def test_reopen_order_without_reason(self, order):
        """Test reopening order without reason."""
        order.status = OrderStatus.CANCELLED.value
        order.save()
        
        service = ReopenOrderService()
        result = service.reopen_order(order.id)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.UNPAID.value
        assert result.reopen_reason is None or result.reopen_reason == ""
    
    def test_reopen_order_sets_reopened_at(self, order):
        """Test reopening sets reopened_at timestamp."""
        order.status = OrderStatus.CANCELLED.value
        order.save()
        
        service = ReopenOrderService()
        result = service.reopen_order(order.id, "Reopen test")
        
        result.refresh_from_db()
        assert result.reopened_at is not None
        assert isinstance(result.reopened_at, datetime)


@pytest.mark.django_db
class TestReopenOrderServiceEdgeCases:
    """Test edge cases for reopen service."""
    
    def test_reopen_multiple_times(self, order):
        """Test reopening order multiple times."""
        order.status = OrderStatus.CANCELLED.value
        order.save()
        
        service = ReopenOrderService()
        
        # First reopen
        result1 = service.reopen_order(order.id, "First reopen")
        result1.refresh_from_db()
        assert result1.status == OrderStatus.UNPAID.value
        
        # Cancel again
        result1.status = OrderStatus.CANCELLED.value
        result1.save()
        
        # Second reopen
        result2 = service.reopen_order(result1.id, "Second reopen")
        result2.refresh_from_db()
        assert result2.status == OrderStatus.UNPAID.value
        assert result2.reopened_from == OrderStatus.CANCELLED.value

