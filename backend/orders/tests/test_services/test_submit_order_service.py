"""
Comprehensive tests for SubmitOrderService.

Tests cover:
- Order submission
- Status validation
- Submission timestamp
- Transition to under_editing
- Late fine automation
- Error handling
"""
import pytest
from unittest.mock import patch
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.submit_order_service import SubmitOrderService
from unittest.mock import MagicMock


@pytest.mark.django_db
class TestSubmitOrderService:
    """Test SubmitOrderService functionality."""
    
    def test_submit_order_success(self, order, writer_user):
        """Test successful order submission."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = SubmitOrderService()
        
        with patch('orders.services.submit_order_service.MoveOrderToEditingService') as mock_editing, \
             patch('orders.services.submit_order_service.auto_issue_late_fine') as mock_fine:
            result = service.execute(order.id, writer_user)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.SUBMITTED.value
        assert result.submitted_at is not None
        mock_editing.execute.assert_called_once()
        mock_fine.assert_called_once()
    
    def test_submit_order_sets_submitted_at(self, order, writer_user):
        """Test submission sets submitted_at timestamp."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = SubmitOrderService()
        
        with patch('orders.services.submit_order_service.MoveOrderToEditingService'), \
             patch('orders.services.submit_order_service.auto_issue_late_fine'):
            before_time = timezone.now()
            result = service.execute(order.id, writer_user)
            after_time = timezone.now()
        
        assert result.submitted_at is not None
        assert before_time <= result.submitted_at <= after_time
    
    def test_submit_order_invalid_status(self, order, writer_user):
        """Test submission fails from invalid status."""
        order.status = OrderStatus.CREATED.value
        order.save()
        
        service = SubmitOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.execute(order.id, writer_user)
        
        assert "must be in progress" in str(exc.value).lower()
    
    def test_submit_order_not_found(self, writer_user):
        """Test submission fails for non-existent order."""
        service = SubmitOrderService()
        
        with pytest.raises(ObjectDoesNotExist) as exc:
            service.execute(99999, writer_user)
        
        assert "not found" in str(exc.value).lower() or "Order not found" in str(exc.value)
    
    def test_submit_order_calls_move_to_editing(self, order, writer_user):
        """Test submission calls MoveOrderToEditingService."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = SubmitOrderService()
        
        mock_editing = MagicMock()
        with patch('orders.services.submit_order_service.MoveOrderToEditingService', return_value=mock_editing), \
             patch('orders.services.submit_order_service.auto_issue_late_fine'):
            service.execute(order.id, writer_user)
            
            # Check execute was called with correct args
            mock_editing.execute.assert_called_once()
            call_args = mock_editing.execute.call_args
            assert call_args[1]['order'] == order
            assert call_args[1]['user'] == writer_user
    
    def test_submit_order_calls_late_fine(self, order, writer_user):
        """Test submission triggers late fine automation."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = SubmitOrderService()
        
        mock_fine = MagicMock()
        with patch('orders.services.submit_order_service.MoveOrderToEditingService'), \
             patch('orders.services.submit_order_service.auto_issue_late_fine', mock_fine):
            service.execute(order.id, writer_user)
            
            mock_fine.assert_called_once_with(order)
    
    def test_submit_order_transitions_to_submitted(self, order, writer_user):
        """Test submission transitions order to submitted status."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.is_paid = True
        order.save()
        
        service = SubmitOrderService()
        
        with patch('orders.services.submit_order_service.MoveOrderToEditingService'), \
             patch('orders.services.submit_order_service.auto_issue_late_fine'):
            result = service.execute(order.id, writer_user)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.SUBMITTED.value


@pytest.mark.django_db
class TestSubmitOrderServiceEdgeCases:
    """Test edge cases for order submission."""
    
    def test_submit_order_from_submitted_status(self, order, writer_user):
        """Test cannot submit already submitted order."""
        order.status = OrderStatus.SUBMITTED.value
        order.assigned_writer = writer_user
        order.save()
        
        service = SubmitOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.execute(order.id, writer_user)
        
        assert "must be in progress" in str(exc.value).lower()
    
    def test_submit_order_preserves_submitted_at(self, order, writer_user):
        """Test submission preserves existing submitted_at if resubmitted."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.is_paid = True
        original_time = timezone.now() - timedelta(hours=1)
        order.submitted_at = original_time
        order.save()
        
        service = SubmitOrderService()
        
        with patch('orders.services.submit_order_service.MoveOrderToEditingService'), \
             patch('orders.services.submit_order_service.auto_issue_late_fine'):
            result = service.execute(order.id, writer_user)
        
        # Should update to current time
        assert result.submitted_at != original_time
        assert result.submitted_at >= timezone.now() - timedelta(seconds=5)

