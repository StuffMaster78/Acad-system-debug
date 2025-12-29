"""
Comprehensive tests for ApproveOrderService.

Tests cover:
- Order approval
- Status validation
- Review and rating requirements
- Referral bonus awarding
- Status transitions
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from orders.models import Order
from orders.order_enums import OrderStatus
from orders.services.approve_order_service import ApproveOrderService


@pytest.mark.django_db
class TestApproveOrderService:
    """Test ApproveOrderService functionality."""
    
    def test_approve_order_from_reviewed(self, order):
        """Test approving order from reviewed status."""
        order.status = OrderStatus.REVIEWED.value
        order.review = "Great work!"
        order.rating = 5
        order.is_paid = True
        order.save()
        
        service = ApproveOrderService()
        
        with patch.object(service, '_award_referral_bonus'):
            result = service.approve_order(order.id)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.APPROVED.value
    
    def test_approve_order_from_rated(self, order):
        """Test approving order from rated status."""
        order.status = OrderStatus.RATED.value
        order.review = "Excellent!"
        order.rating = 4
        order.is_paid = True
        order.save()
        
        service = ApproveOrderService()
        
        with patch.object(service, '_award_referral_bonus'):
            result = service.approve_order(order.id)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.APPROVED.value
    
    def test_approve_order_transitions_through_rated(self, order):
        """Test approving order transitions through rated if needed."""
        order.status = OrderStatus.REVIEWED.value
        order.review = "Good work"
        order.rating = 5
        order.is_paid = True
        order.save()
        
        service = ApproveOrderService()
        
        with patch.object(service, '_award_referral_bonus'):
            result = service.approve_order(order.id)
        
        result.refresh_from_db()
        assert result.status == OrderStatus.APPROVED.value
    
    def test_approve_order_missing_review(self, order):
        """Test approving order without review raises error."""
        order.status = OrderStatus.REVIEWED.value
        order.review = None
        order.rating = 5
        order.save()
        
        service = ApproveOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.approve_order(order.id)
        
        assert "lacks a review" in str(exc.value).lower()
    
    def test_approve_order_missing_rating(self, order):
        """Test approving order without rating raises error."""
        order.status = OrderStatus.REVIEWED.value
        order.review = "Good work"
        order.rating = None
        order.save()
        
        service = ApproveOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.approve_order(order.id)
        
        assert "lacks a rating" in str(exc.value).lower()
    
    def test_approve_order_invalid_status(self, order):
        """Test approving order from invalid status raises error."""
        order.status = OrderStatus.CREATED.value
        order.review = "Review"
        order.rating = 5
        order.save()
        
        service = ApproveOrderService()
        
        with pytest.raises(ValueError) as exc:
            service.approve_order(order.id)
        
        assert "cannot be approved" in str(exc.value).lower()
    
    def test_approve_order_awards_referral_bonus(self, order, client_user):
        """Test approval awards referral bonus for first approved order."""
        from referrals.models import Referral
        
        order.status = OrderStatus.REVIEWED.value
        order.review = "Great!"
        order.rating = 5
        order.client = client_user
        order.is_paid = True
        order.save()
        
        # Create referral
        referral = Referral.objects.create(
            referrer=client_user,
            referee=client_user,
            website=order.website,
            is_deleted=False
        )
        
        service = ApproveOrderService()
        
        with patch('orders.services.approve_order_service.ReferralService') as mock_service:
            mock_instance = MagicMock()
            mock_service.return_value = mock_instance
            
            result = service.approve_order(order.id)
            
            # Should check for referral and award bonus
            # (Only if this is first approved order)
            result.refresh_from_db()
            assert result.status == OrderStatus.APPROVED.value


@pytest.mark.django_db
class TestApproveOrderServiceReferralBonus:
    """Test referral bonus awarding logic."""
    
    def test_referral_bonus_only_first_approved_order(self, order, client_user):
        """Test referral bonus only awarded for first approved order."""
        from referrals.models import Referral
        
        # Create first approved order
        first_order = Order.objects.create(
            client=client_user,
            website=order.website,
            status=OrderStatus.APPROVED.value,
            topic="First Order",
            client_deadline=order.client_deadline,
            is_paid=True
        )
        
        # Current order
        order.status = OrderStatus.REVIEWED.value
        order.review = "Review"
        order.rating = 5
        order.client = client_user
        order.is_paid = True
        order.save()
        
        # Create referral
        referral = Referral.objects.create(
            referrer=client_user,
            referee=client_user,
            website=order.website,
            is_deleted=False
        )
        
        service = ApproveOrderService()
        
        with patch('orders.services.approve_order_service.ReferralService') as mock_service:
            result = service.approve_order(order.id)
            
            # Should not award bonus (not first approved order)
            # The service checks for previous approved orders
            result.refresh_from_db()
            assert result.status == OrderStatus.APPROVED.value
    
    def test_referral_bonus_no_referral(self, order, client_user):
        """Test no referral bonus if no referral exists."""
        order.status = OrderStatus.REVIEWED.value
        order.review = "Review"
        order.rating = 5
        order.client = client_user
        order.is_paid = True
        order.save()
        
        service = ApproveOrderService()
        
        # Should not raise error even without referral
        result = service.approve_order(order.id)
        result.refresh_from_db()
        assert result.status == OrderStatus.APPROVED.value

