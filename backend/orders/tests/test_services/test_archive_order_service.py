"""
Comprehensive tests for ArchiveOrderService.

Tests cover:
- Archiving orders
- Status validation
- Status transitions
"""
import pytest

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.archive_order_service import ArchiveOrderService


@pytest.mark.django_db
class TestArchiveOrderService:
    """Test ArchiveOrderService functionality."""
    
    def test_archive_order_success(self, order, admin_user):
        """Test successfully archiving an approved order."""
        order.status = OrderStatus.APPROVED.value
        order.save()
        
        service = ArchiveOrderService()
        result = service.archive_order(order.id, user=admin_user)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.ARCHIVED.value
    
    def test_archive_order_wrong_status(self, order, admin_user):
        """Test archiving order from wrong status raises error."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        service = ArchiveOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.archive_order(order.id, user=admin_user)
        
        assert "cannot be archived" in str(exc.value).lower()
    
    def test_archive_order_without_user(self, order):
        """Test archiving order without user (system archiving)."""
        order.status = OrderStatus.APPROVED.value
        order.save()
        
        service = ArchiveOrderService()
        result = service.archive_order(order.id, user=None)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.ARCHIVED.value
    
    def test_archive_order_transitions_to_archived(self, order, admin_user):
        """Test archiving transitions order to archived status."""
        order.status = OrderStatus.APPROVED.value
        order.save()
        
        service = ArchiveOrderService()
        result = service.archive_order(order.id, user=admin_user)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.ARCHIVED.value

