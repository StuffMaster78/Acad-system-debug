"""
Comprehensive tests for OrderFlagsService.

Tests cover:
- Flag evaluation
- Flag application
- Urgent order detection
- First/returning client detection
- High value order detection
- Preferred order detection
"""
import pytest
from datetime import timedelta
from django.utils import timezone

from orders.models import Order
from orders.order_enums import OrderFlags
from orders.services.order_flags_service import OrderFlagsService


@pytest.mark.django_db
class TestOrderFlagsService:
    """Test OrderFlagsService functionality."""
    
    def test_evaluate_flags_urgent(self, order, client_user):
        """Test urgent flag is set for orders with deadline < 24 hours."""
        order.client = client_user
        order.client_deadline = timezone.now() + timedelta(hours=12)
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.URGENT_ORDER in flags
    
    def test_evaluate_flags_not_urgent(self, order, client_user):
        """Test urgent flag not set for orders with deadline > 24 hours."""
        order.client = client_user
        order.client_deadline = timezone.now() + timedelta(days=3)
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.URGENT_ORDER not in flags
    
    def test_evaluate_flags_first_order(self, order, client_user):
        """Test first order flag for new client."""
        order.client = client_user
        order.save()
        
        # No other orders for this client
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.FIRST_CLIENT_ORDER in flags
    
    def test_evaluate_flags_returning_client(self, order, client_user):
        """Test returning client flag when client has previous orders."""
        # Create previous order
        Order.objects.create(
            client=client_user,
            website=order.website,
            topic="Previous Order",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.COMPLETED.value
        )
        
        order.client = client_user
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.RETURNING_CLIENT_ORDER in flags
        assert OrderFlags.FIRST_CLIENT_ORDER not in flags
    
    def test_evaluate_flags_high_value(self, order, client_user):
        """Test high value flag for orders >= $300."""
        order.client = client_user
        order.total_price = 350.00
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.HIGH_VALUE_ORDER in flags
    
    def test_evaluate_flags_not_high_value(self, order, client_user):
        """Test high value flag not set for orders < $300."""
        order.client = client_user
        order.total_price = 200.00
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.HIGH_VALUE_ORDER not in flags
    
    def test_evaluate_flags_preferred(self, order, client_user):
        """Test preferred flag when client is preferred."""
        client_user.is_preferred = True
        client_user.save()
        
        order.client = client_user
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert OrderFlags.PREFERRED_ORDER in flags
    
    def test_apply_flags_persists(self, order, client_user):
        """Test applying flags persists to database."""
        order.client = client_user
        order.client_deadline = timezone.now() + timedelta(hours=12)
        order.total_price = 350.00
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.apply_flags(persist=True)
        
        order.refresh_from_db()
        assert len(order.flags) > 0
        assert OrderFlags.URGENT_ORDER.value in order.flags
        assert OrderFlags.HIGH_VALUE_ORDER.value in order.flags
    
    def test_apply_flags_no_persist(self, order, client_user):
        """Test applying flags without persisting."""
        order.client = client_user
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.apply_flags(persist=False)
        
        # Flags should be set on order object but not saved
        assert len(order.flags) > 0
        # But database might not be updated (depends on implementation)
    
    def test_multiple_flags(self, order, client_user):
        """Test multiple flags can be set simultaneously."""
        # Create previous order to make returning client
        Order.objects.create(
            client=client_user,
            website=order.website,
            topic="Previous",
            client_deadline=timezone.now() + timedelta(days=1),
            status=OrderStatus.COMPLETED.value
        )
        
        order.client = client_user
        order.client_deadline = timezone.now() + timedelta(hours=12)
        order.total_price = 400.00
        order.save()
        
        service = OrderFlagsService(order)
        flags = service.evaluate_flags()
        
        assert len(flags) >= 3  # Urgent, Returning, High Value
        assert OrderFlags.URGENT_ORDER in flags
        assert OrderFlags.RETURNING_CLIENT_ORDER in flags
        assert OrderFlags.HIGH_VALUE_ORDER in flags

