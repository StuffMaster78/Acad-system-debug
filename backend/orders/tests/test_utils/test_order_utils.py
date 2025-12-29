"""
Comprehensive tests for order_utils.

Tests cover:
- get_order_by_id
- save_order
- get_orders_by_status_older_than
- Audit logging
"""
import pytest
from datetime import datetime, timedelta
from django.http import Http404
from django.utils import timezone

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.utils.order_utils import (
    get_order_by_id,
    save_order,
    get_orders_by_status_older_than
)
from authentication.models import AuditLog


@pytest.mark.django_db
class TestGetOrderById:
    """Test get_order_by_id utility."""
    
    def test_get_order_by_id_success(self, order, client_user):
        """Test successfully getting order by ID."""
        result = get_order_by_id(order.id, user=client_user)
        
        assert result.id == order.id
        assert result == order
    
    def test_get_order_by_id_without_user(self, order):
        """Test getting order without user."""
        result = get_order_by_id(order.id)
        
        assert result.id == order.id
    
    def test_get_order_by_id_not_found(self, client_user):
        """Test getting non-existent order raises 404."""
        with pytest.raises(Http404):
            get_order_by_id(99999, user=client_user)
    
    def test_get_order_by_id_excludes_soft_deleted(self, order, client_user):
        """Test get_order_by_id excludes soft-deleted orders by default."""
        order.is_deleted = True
        order.save()
        
        with pytest.raises(Http404):
            get_order_by_id(order.id, user=client_user)
    
    def test_get_order_by_id_includes_soft_deleted(self, order, client_user):
        """Test get_order_by_id includes soft-deleted when flag set."""
        order.is_deleted = True
        order.save()
        
        result = get_order_by_id(order.id, user=client_user, check_soft_deleted=False)
        
        assert result.id == order.id
        assert result.is_deleted is True
    
    def test_get_order_by_id_logs_access(self, order, client_user):
        """Test getting order logs access."""
        initial_count = AuditLog.objects.count()
        
        get_order_by_id(order.id, user=client_user)
        
        assert AuditLog.objects.count() == initial_count + 1
        log = AuditLog.objects.latest('id')
        assert log.action == "order_viewed"
        assert log.related_object == order


@pytest.mark.django_db
class TestSaveOrder:
    """Test save_order utility."""
    
    def test_save_order_success(self, order):
        """Test successfully saving order."""
        old_updated_at = order.updated_at
        order.status = OrderStatus.IN_PROGRESS.value
        
        save_order(order)
        
        order.refresh_from_db()
        assert order.status == OrderStatus.IN_PROGRESS.value
        assert order.updated_at > old_updated_at
    
    def test_save_order_with_user_and_event(self, order, admin_user):
        """Test saving order with user and event logs audit."""
        initial_count = AuditLog.objects.count()
        
        save_order(order, user=admin_user, event="test_event", notes="Test notes")
        
        assert AuditLog.objects.count() == initial_count + 1
        log = AuditLog.objects.latest('id')
        assert log.action == "test_event"
        assert log.notes == "Test notes"
    
    def test_save_order_without_user(self, order):
        """Test saving order without user doesn't log."""
        initial_count = AuditLog.objects.count()
        
        save_order(order)
        
        # Should not create audit log without user
        assert AuditLog.objects.count() == initial_count
    
    def test_save_order_updates_timestamp(self, order):
        """Test save_order updates updated_at timestamp."""
        old_timestamp = order.updated_at
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(0.1)
        
        save_order(order)
        
        order.refresh_from_db()
        assert order.updated_at > old_timestamp


@pytest.mark.django_db
class TestGetOrdersByStatusOlderThan:
    """Test get_orders_by_status_older_than utility."""
    
    def test_get_orders_by_status_older_than(self, client_user, website):
        """Test getting orders by status older than cutoff."""
        cutoff_date = timezone.now() - timedelta(days=5)
        
        # Create old order
        old_order = Order.objects.create(
            client=client_user,
            website=website,
            topic="Old Order",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.COMPLETED.value,
            updated_at=cutoff_date - timedelta(days=1)
        )
        
        # Create new order
        new_order = Order.objects.create(
            client=client_user,
            website=website,
            topic="New Order",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.COMPLETED.value,
            updated_at=timezone.now()
        )
        
        results = get_orders_by_status_older_than(OrderStatus.COMPLETED.value, cutoff_date)
        
        assert old_order in results
        assert new_order not in results
    
    def test_get_orders_by_status_older_than_empty(self, client_user, website):
        """Test getting orders when none match."""
        cutoff_date = timezone.now() - timedelta(days=10)
        
        # Create new order (not old enough)
        Order.objects.create(
            client=client_user,
            website=website,
            topic="New Order",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.COMPLETED.value,
            updated_at=timezone.now()
        )
        
        results = get_orders_by_status_older_than(OrderStatus.COMPLETED.value, cutoff_date)
        
        assert results.count() == 0
    
    def test_get_orders_by_status_older_than_different_status(self, client_user, website):
        """Test filtering by status works correctly."""
        cutoff_date = timezone.now() - timedelta(days=5)
        
        # Create completed order
        completed_order = Order.objects.create(
            client=client_user,
            website=website,
            topic="Completed",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.COMPLETED.value,
            updated_at=cutoff_date - timedelta(days=1)
        )
        
        # Create pending order
        pending_order = Order.objects.create(
            client=client_user,
            website=website,
            topic="Pending",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.PENDING.value,
            updated_at=cutoff_date - timedelta(days=1)
        )
        
        results = get_orders_by_status_older_than(OrderStatus.COMPLETED.value, cutoff_date)
        
        assert completed_order in results
        assert pending_order not in results

