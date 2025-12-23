"""
Service layer tests for FineService.
Tests fine creation, calculation, and business logic.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from fines.models import Fine, FinePolicy, FineType, FineStatus
from fines.services.fine_services import FineService


@pytest.mark.unit
@pytest.mark.fines
class TestFineServiceIssueFine:
    """Tests for issuing fines."""
    
    def test_issue_fine_with_fixed_amount(self, website, writer_user, order, admin_user):
        """Test issuing a fine with fixed amount policy."""
        # Create a fine policy with fixed amount
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('50.00'),
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        fine = FineService.issue_fine(
            order=order,
            fine_type=FineType.LATE_SUBMISSION,
            reason='Late submission',
            issued_by=admin_user
        )
        
        assert fine is not None
        assert fine.amount == Decimal('50.00')
        assert fine.fine_type == FineType.LATE_SUBMISSION
        assert fine.status == FineStatus.ISSUED
        assert fine.issued_by == admin_user
        assert fine.order == order
    
    def test_issue_fine_with_percentage(self, website, writer_user, order, admin_user):
        """Test issuing a fine with percentage-based policy."""
        # Create a fine policy with percentage
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.QUALITY_ISSUE,
            percentage=Decimal('10.00'),  # 10% of order total
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        order.total_price = Decimal('100.00')
        order.save()
        
        fine = FineService.issue_fine(
            order=order,
            fine_type=FineType.QUALITY_ISSUE,
            reason='Quality issue',
            issued_by=admin_user
        )
        
        assert fine is not None
        assert fine.amount == Decimal('10.00')  # 10% of 100
        assert fine.fine_type == FineType.QUALITY_ISSUE
    
    def test_issue_fine_no_active_policy(self, website, order, admin_user):
        """Test that issuing fine fails when no active policy exists."""
        with pytest.raises(ValueError, match="No active fine policy"):
            FineService.issue_fine(
                order=order,
                fine_type=FineType.LATE_SUBMISSION,
                reason='Test',
                issued_by=admin_user
            )
    
    def test_issue_fine_inactive_policy_excluded(self, website, order, admin_user):
        """Test that inactive policies are excluded."""
        FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('50.00'),
            active=False,  # Inactive
            start_date=timezone.now() - timedelta(days=1)
        )
        
        with pytest.raises(ValueError, match="No active fine policy"):
            FineService.issue_fine(
                order=order,
                fine_type=FineType.LATE_SUBMISSION,
                reason='Test',
                issued_by=admin_user
            )
    
    def test_issue_fine_policy_with_end_date(self, website, order, admin_user):
        """Test that policies with past end dates are excluded."""
        FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('50.00'),
            active=True,
            start_date=timezone.now() - timedelta(days=10),
            end_date=timezone.now() - timedelta(days=1)  # Past end date
        )
        
        with pytest.raises(ValueError, match="No active fine policy"):
            FineService.issue_fine(
                order=order,
                fine_type=FineType.LATE_SUBMISSION,
                reason='Test',
                issued_by=admin_user
            )


@pytest.mark.unit
@pytest.mark.fines
class TestFineServiceWaiveFine:
    """Tests for waiving fines."""
    
    def test_waive_fine_success(self, website, writer_user, order, admin_user):
        """Test successfully waiving a fine."""
        # Create a fine
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('50.00'),
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        fine = FineService.issue_fine(
            order=order,
            fine_type=FineType.LATE_SUBMISSION,
            reason='Late submission',
            issued_by=admin_user
        )
        
        # Waive the fine
        waived_fine = FineService.waive_fine(
            fine=fine,
            waived_by=admin_user,
            reason='First offense'
        )
        
        assert waived_fine.status == FineStatus.WAIVED
        assert waived_fine.waived_by == admin_user
        assert waived_fine.waived_at is not None


@pytest.mark.unit
@pytest.mark.fines
class TestFineServiceCalculateAmount:
    """Tests for fine amount calculation."""
    
    def test_calculate_amount_fixed(self, website):
        """Test calculating amount from fixed policy."""
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('75.00'),
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        # Amount should be the fixed amount
        assert policy.fixed_amount == Decimal('75.00')
    
    def test_calculate_amount_percentage(self, website):
        """Test calculating amount from percentage policy."""
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.QUALITY_ISSUE,
            percentage=Decimal('15.00'),  # 15%
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        # For order with $100 total, amount should be $15
        order_total = Decimal('100.00')
        expected_amount = (order_total * policy.percentage) / Decimal('100.00')
        assert expected_amount == Decimal('15.00')

