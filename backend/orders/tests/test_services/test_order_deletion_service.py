"""
Comprehensive tests for OrderDeletionService.

Tests cover:
- Soft deletion
- Hard deletion
- Restore functionality
- Permission checks
- Website scoping
"""
import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.order_deletion_service import OrderDeletionService


@pytest.mark.django_db
class TestOrderDeletionService:
    """Test OrderDeletionService functionality."""
    
    def test_soft_delete_by_admin(self, order, admin_user, website):
        """Test admin can soft delete order."""
        order.status = OrderStatus.PAID.value
        order.save()
        
        service = OrderDeletionService(website=website)
        result = service.soft_delete(user=admin_user, order=order, reason="Test deletion")
        
        assert result.was_deleted is True
        assert result.hard is False
        order.refresh_from_db()
        assert order.is_deleted is True
    
    def test_soft_delete_by_client_unpaid(self, order, client_user, website):
        """Test client can soft delete unpaid order."""
        order.status = OrderStatus.UNPAID.value
        order.client = client_user
        order.save()
        
        service = OrderDeletionService(website=website)
        result = service.soft_delete(user=client_user, order=order, reason="Changed mind")
        
        assert result.was_deleted is True
        order.refresh_from_db()
        assert order.is_deleted is True
    
    def test_soft_delete_by_client_paid_denied(self, order, client_user, website):
        """Test client cannot delete paid order."""
        order.status = OrderStatus.PAID.value
        order.client = client_user
        order.save()
        
        service = OrderDeletionService(website=website)
        
        with pytest.raises(PermissionDenied) as exc:
            service.soft_delete(user=client_user, order=order, reason="Test")
        
        assert "can only delete unpaid" in str(exc.value).lower()
    
    def test_soft_delete_already_deleted(self, order, admin_user, website):
        """Test soft deleting already deleted order is idempotent."""
        order.is_deleted = True
        order.save()
        
        service = OrderDeletionService(website=website)
        result = service.soft_delete(user=admin_user, order=order)
        
        assert result.was_deleted is False  # Already deleted
    
    def test_restore_by_admin(self, order, admin_user, website):
        """Test admin can restore deleted order."""
        order.is_deleted = True
        order.save()
        
        service = OrderDeletionService(website=website)
        order_id = service.restore(user=admin_user, order=order)
        
        assert order_id == order.id
        order.refresh_from_db()
        assert order.is_deleted is False
    
    def test_restore_by_client_own_order(self, order, client_user, website):
        """Test client can restore own deleted order."""
        order.is_deleted = True
        order.client = client_user
        order.save()
        
        service = OrderDeletionService(website=website)
        order_id = service.restore(user=client_user, order=order)
        
        assert order_id == order.id
        order.refresh_from_db()
        assert order.is_deleted is False
    
    def test_restore_not_deleted_raises_error(self, order, admin_user, website):
        """Test restoring non-deleted order raises error."""
        order.is_deleted = False
        order.save()
        
        service = OrderDeletionService(website=website)
        
        with pytest.raises(ValidationError) as exc:
            service.restore(user=admin_user, order=order)
        
        assert "not deleted" in str(exc.value).lower()
    
    def test_hard_delete_by_admin(self, order, admin_user, website):
        """Test admin can hard delete order."""
        service = OrderDeletionService(website=website)
        result = service.hard_delete_by_id(user=admin_user, order_id=order.id)
        
        assert result.was_deleted is True
        assert result.hard is True
        assert not Order.objects.filter(id=order.id).exists()
    
    def test_hard_delete_by_client_denied(self, order, client_user, website):
        """Test client cannot hard delete order."""
        service = OrderDeletionService(website=website)
        
        with pytest.raises(PermissionDenied) as exc:
            service.hard_delete_by_id(user=client_user, order_id=order.id)
        
        assert "only staff" in str(exc.value).lower()
    
    def test_cross_website_access_denied(self, order, admin_user, website, website2):
        """Test cannot delete order from different website."""
        order.website = website
        order.save()
        
        service = OrderDeletionService(website=website2)
        
        with pytest.raises(PermissionDenied) as exc:
            service.soft_delete(user=admin_user, order=order)
        
        assert "cross-tenant" in str(exc.value).lower() or "not allowed" in str(exc.value).lower()

