"""
Comprehensive tests for OrderDeadlineService.

Tests cover:
- Updating deadlines
- Deadline validation
- Audit logging
- Edge cases
"""
import pytest
from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone

from orders.models import Order
from orders.services.order_deadline_service import OrderDeadlineService


@pytest.mark.django_db
class TestOrderDeadlineService:
    """Test OrderDeadlineService functionality."""
    
    def test_update_deadline_success(self, order, admin_user):
        """Test successfully updating deadline."""
        new_deadline = timezone.now() + timedelta(days=7)
        old_deadline = order.client_deadline
        
        with patch('orders.services.order_deadline_service.AuditLogService') as mock_audit:
            result = OrderDeadlineService.update_deadline(
                order=order,
                new_deadline=new_deadline,
                actor=admin_user,
                reason="Client requested extension"
            )
        
        result.refresh_from_db()
        assert result.client_deadline == new_deadline
    
    def test_update_deadline_past_date_raises_error(self, order, admin_user):
        """Test updating deadline to past date raises error."""
        past_deadline = timezone.now() - timedelta(days=1)
        
        with pytest.raises(ValueError) as exc:
            OrderDeadlineService.update_deadline(
                order=order,
                new_deadline=past_deadline,
                actor=admin_user
            )
        
        assert "must be in the future" in str(exc.value).lower()
    
    def test_update_deadline_same_date_no_op(self, order, admin_user):
        """Test updating to same deadline is no-op."""
        current_deadline = order.client_deadline
        
        result = OrderDeadlineService.update_deadline(
            order=order,
            new_deadline=current_deadline,
            actor=admin_user
        )
        
        assert result == order  # Returns same object
    
    def test_update_deadline_logs_audit(self, order, admin_user):
        """Test deadline update logs audit."""
        new_deadline = timezone.now() + timedelta(days=5)
        old_deadline = order.client_deadline
        
        mock_audit = MagicMock()
        with patch('orders.services.order_deadline_service.AuditLogService', mock_audit):
            OrderDeadlineService.update_deadline(
                order=order,
                new_deadline=new_deadline,
                actor=admin_user,
                reason="Test reason"
            )
        
        mock_audit.log_auto.assert_called_once()
    
    def test_update_deadline_audit_failure_doesnt_block(self, order, admin_user):
        """Test audit logging failure doesn't block deadline update."""
        new_deadline = timezone.now() + timedelta(days=3)
        
        with patch('orders.services.order_deadline_service.AuditLogService.log_auto', side_effect=Exception("Audit failed")):
            result = OrderDeadlineService.update_deadline(
                order=order,
                new_deadline=new_deadline,
                actor=admin_user
            )
        
        result.refresh_from_db()
        assert result.client_deadline == new_deadline  # Still updated

