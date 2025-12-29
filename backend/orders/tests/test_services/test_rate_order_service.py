"""
Comprehensive tests for RateOrderService.

Tests cover:
- Rating orders
- Rating validation
- Status requirements
- Status transitions
"""
import pytest

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.rate_order_service import RateOrderService


@pytest.mark.django_db
class TestRateOrderService:
    """Test RateOrderService functionality."""
    
    def test_rate_order_success(self, order, client_user):
        """Test successfully rating an order."""
        order.status = OrderStatus.REVIEWED.value
        order.save()
        
        service = RateOrderService()
        result = service.rate_order(order.id, rating=5, user=client_user)
        
        result.refresh_from_db()
        assert result.rating == 5
        assert result.status == OrderStatus.RATED.value
    
    def test_rate_order_valid_ratings(self, order, client_user):
        """Test rating with valid rating values."""
        order.status = OrderStatus.REVIEWED.value
        order.save()
        
        service = RateOrderService()
        
        for rating in [1, 2, 3, 4, 5]:
            order.status = OrderStatus.REVIEWED.value
            order.save()
            
            result = service.rate_order(order.id, rating=rating, user=client_user)
            assert result.rating == rating
    
    def test_rate_order_invalid_rating_too_low(self, order, client_user):
        """Test rating with rating below 1 raises error."""
        order.status = OrderStatus.REVIEWED.value
        order.save()
        
        service = RateOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.rate_order(order.id, rating=0, user=client_user)
        
        assert "between 1 and 5" in str(exc.value).lower()
    
    def test_rate_order_invalid_rating_too_high(self, order, client_user):
        """Test rating with rating above 5 raises error."""
        order.status = OrderStatus.REVIEWED.value
        order.save()
        
        service = RateOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.rate_order(order.id, rating=6, user=client_user)
        
        assert "between 1 and 5" in str(exc.value).lower()
    
    def test_rate_order_wrong_status(self, order, client_user):
        """Test rating order from wrong status raises error."""
        order.status = OrderStatus.SUBMITTED.value
        order.save()
        
        service = RateOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.rate_order(order.id, rating=5, user=client_user)
        
        assert "can only be rated after review" in str(exc.value).lower()
    
    def test_rate_order_transitions_to_rated(self, order, client_user):
        """Test rating transitions order to rated status."""
        order.status = OrderStatus.REVIEWED.value
        order.save()
        
        service = RateOrderService()
        result = service.rate_order(order.id, rating=4, user=client_user)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.RATED.value
    
    def test_rate_order_without_user(self, order):
        """Test rating order without user (system rating)."""
        order.status = OrderStatus.REVIEWED.value
        order.save()
        
        service = RateOrderService()
        result = service.rate_order(order.id, rating=5, user=None)
        
        result.refresh_from_db()
        assert result.rating == 5
        assert result.status == OrderStatus.RATED.value

