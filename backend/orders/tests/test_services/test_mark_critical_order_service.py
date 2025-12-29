"""
Comprehensive tests for MarkCriticalOrderService.

Tests cover:
- Marking order as critical
- Critical threshold calculation
- Status updates based on deadline
- Edge cases
"""
import pytest
from datetime import datetime, timedelta
from django.utils import timezone

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.mark_critical_order_service import MarkCriticalOrderService
from order_configs.models import CriticalDeadlineSetting


@pytest.mark.django_db
class TestMarkCriticalOrderService:
    """Test MarkCriticalOrderService functionality."""
    
    def test_mark_critical_success(self, order):
        """Test successfully marking order as critical."""
        order.is_critical = False
        order.save()
        
        service = MarkCriticalOrderService()
        result = service.mark_critical(order.id)
        
        result.refresh_from_db()
        assert result.is_critical is True
    
    def test_mark_critical_already_critical(self, order):
        """Test marking already critical order raises error."""
        order.is_critical = True
        order.save()
        
        service = MarkCriticalOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.mark_critical(order.id)
        
        assert "already critical" in str(exc.value).lower()
    
    def test_get_critical_threshold_with_config(self, website):
        """Test getting critical threshold from config."""
        CriticalDeadlineSetting.objects.create(
            website=website,
            critical_deadline_threshold_hours=12
        )
        
        threshold = MarkCriticalOrderService.get_critical_threshold()
        assert threshold == 12
    
    def test_get_critical_threshold_no_config(self):
        """Test getting critical threshold default when no config."""
        # Delete any existing configs
        CriticalDeadlineSetting.objects.all().delete()
        
        threshold = MarkCriticalOrderService.get_critical_threshold()
        assert threshold == 8  # Default fallback
    
    def test_update_order_status_based_on_deadline_critical(self, order):
        """Test updating order status to critical when deadline is close."""
        # Set deadline within threshold (8 hours default)
        order.client_deadline = timezone.now() + timedelta(hours=6)
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        MarkCriticalOrderService.update_order_status_based_on_deadline(order)
        
        order.refresh_from_db()
        assert order.status == OrderStatus.CRITICAL.value
    
    def test_update_order_status_based_on_deadline_not_critical(self, order):
        """Test order status not changed when deadline is far."""
        # Set deadline beyond threshold
        order.client_deadline = timezone.now() + timedelta(days=2)
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        MarkCriticalOrderService.update_order_status_based_on_deadline(order)
        
        order.refresh_from_db()
        assert order.status == OrderStatus.IN_PROGRESS.value
    
    def test_update_order_status_no_deadline(self, order):
        """Test update does nothing when order has no deadline."""
        order.client_deadline = None
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        original_status = order.status
        
        MarkCriticalOrderService.update_order_status_based_on_deadline(order)
        
        order.refresh_from_db()
        assert order.status == original_status  # Unchanged
    
    def test_update_order_status_removes_critical_when_far(self, order):
        """Test order status changed from critical when deadline is far."""
        # Set deadline far in future
        order.client_deadline = timezone.now() + timedelta(days=3)
        order.status = OrderStatus.CRITICAL.value
        order.save()
        
        MarkCriticalOrderService.update_order_status_based_on_deadline(order)
        
        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING.value  # Changed from CRITICAL


@pytest.mark.django_db
class TestMarkCriticalOrderServiceEdgeCases:
    """Test edge cases for critical order service."""
    
    def test_critical_threshold_custom_value(self, website):
        """Test custom critical threshold value."""
        CriticalDeadlineSetting.objects.create(
            website=website,
            critical_deadline_threshold_hours=24
        )
        
        threshold = MarkCriticalOrderService.get_critical_threshold()
        assert threshold == 24
    
    def test_update_status_exactly_at_threshold(self, order):
        """Test status update when deadline is exactly at threshold."""
        # Set deadline exactly at threshold (8 hours)
        order.client_deadline = timezone.now() + timedelta(hours=8)
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        MarkCriticalOrderService.update_order_status_based_on_deadline(order)
        
        order.refresh_from_db()
        # Should be critical (<= threshold)
        assert order.status == OrderStatus.CRITICAL.value
    
    def test_update_status_just_over_threshold(self, order):
        """Test status not changed when just over threshold."""
        # Set deadline just over threshold (8.1 hours)
        order.client_deadline = timezone.now() + timedelta(hours=8, minutes=6)
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        MarkCriticalOrderService.update_order_status_based_on_deadline(order)
        
        order.refresh_from_db()
        # Should not be critical (> threshold)
        assert order.status == OrderStatus.IN_PROGRESS.value

