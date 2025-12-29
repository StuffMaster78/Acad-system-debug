"""
Comprehensive tests for ReviewOrderService.

Tests cover:
- Submitting reviews
- Review validation
- Status requirements
- Empty review handling
"""
import pytest

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.review_order_service import ReviewOrderService


@pytest.mark.django_db
class TestReviewOrderService:
    """Test ReviewOrderService functionality."""
    
    def test_submit_review_success(self, order):
        """Test successfully submitting a review."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = ReviewOrderService()
        result = service.submit_review(order.id, "Great work! Very satisfied.")
        
        result.refresh_from_db()
        assert result.review == "Great work! Very satisfied."
    
    def test_submit_review_strips_whitespace(self, order):
        """Test review text is stripped of whitespace."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = ReviewOrderService()
        result = service.submit_review(order.id, "  Great work!  ")
        
        result.refresh_from_db()
        assert result.review == "Great work!"
    
    def test_submit_review_empty_string(self, order):
        """Test submitting empty review raises error."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = ReviewOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.submit_review(order.id, "")
        
        assert "cannot be empty" in str(exc.value).lower()
    
    def test_submit_review_whitespace_only(self, order):
        """Test submitting whitespace-only review raises error."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = ReviewOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.submit_review(order.id, "   ")
        
        assert "cannot be empty" in str(exc.value).lower()
    
    def test_submit_review_wrong_status(self, order):
        """Test submitting review from wrong status raises error."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        service = ReviewOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.submit_review(order.id, "Good work")
        
        assert "cannot be reviewed" in str(exc.value).lower()
    
    def test_submit_review_long_text(self, order):
        """Test submitting long review text."""
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        long_review = "This is a very long review. " * 50
        
        service = ReviewOrderService()
        result = service.submit_review(order.id, long_review)
        
        result.refresh_from_db()
        assert len(result.review) > 1000

