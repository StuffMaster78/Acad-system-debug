"""
Integration tests for fine imposition and dispute workflow.
Tests the complete flow from fine issuance to dispute resolution.
"""
import pytest
from decimal import Decimal
from django.utils import timezone

from orders.models import Order
from fines.models import Fine, FinePolicy, FineType, FineStatus, FineAppeal
from fines.services.fine_services import FineService


@pytest.mark.integration
@pytest.mark.e2e
class TestFineImpositionWorkflow:
    """Tests for fine imposition workflow."""
    
    def test_fine_imposition_to_appeal(self, website, writer_user, order, admin_user):
        """Test complete flow from fine imposition to appeal."""
        # Create fine policy
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('50.00'),
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        # Issue fine
        fine = FineService.issue_fine(
            order=order,
            fine_type=FineType.LATE_SUBMISSION,
            reason='Late submission',
            issued_by=admin_user
        )
        
        assert fine.status == FineStatus.ISSUED
        assert fine.amount == Decimal('50.00')
        
        # Writer creates appeal
        appeal = FineAppeal.objects.create(
            fine=fine,
            writer=writer_user,
            reason='I submitted on time, there was a system error',
            status='pending'
        )
        
        assert appeal.status == 'pending'
        assert appeal.fine == fine
        assert appeal.writer == writer_user
    
    def test_fine_appeal_approval_workflow(self, website, writer_user, order, admin_user):
        """Test fine appeal approval workflow."""
        # Create and issue fine
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
        
        # Create appeal
        appeal = FineAppeal.objects.create(
            fine=fine,
            writer=writer_user,
            reason='Valid reason',
            status='pending'
        )
        
        # Approve appeal
        waived_fine = FineService.waive_fine(
            fine=fine,
            waived_by=admin_user,
            reason='Appeal approved'
        )
        
        assert waived_fine.status == FineStatus.WAIVED
        appeal.refresh_from_db()
        assert appeal.status == 'approved'
    
    def test_fine_appeal_rejection_workflow(self, website, writer_user, order, admin_user):
        """Test fine appeal rejection workflow."""
        # Create and issue fine
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
        
        # Create appeal
        appeal = FineAppeal.objects.create(
            fine=fine,
            writer=writer_user,
            reason='Invalid reason',
            status='pending'
        )
        
        # Reject appeal (fine remains active)
        appeal.status = 'rejected'
        appeal.save()
        
        fine.refresh_from_db()
        assert fine.status == FineStatus.ISSUED  # Still issued, not waived
        assert appeal.status == 'rejected'


@pytest.mark.integration
@pytest.mark.e2e
class TestFineMultipleOrders:
    """Tests for fine handling across multiple orders."""
    
    def test_multiple_fines_for_writer(self, website, writer_user, admin_user):
        """Test issuing multiple fines for the same writer."""
        # Create multiple orders
        order1 = Order.objects.create(
            client=writer_user,  # Using writer as client for simplicity
            website=website,
            topic='Order 1',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            status='completed'
        )
        
        order2 = Order.objects.create(
            client=writer_user,
            website=website,
            topic='Order 2',
            number_of_pages=3,
            total_price=Decimal('50.00'),
            status='completed'
        )
        
        # Create fine policy
        policy = FinePolicy.objects.create(
            website=website,
            fine_type=FineType.LATE_SUBMISSION,
            fixed_amount=Decimal('25.00'),
            active=True,
            start_date=timezone.now() - timedelta(days=1)
        )
        
        # Issue fines for both orders
        fine1 = FineService.issue_fine(
            order=order1,
            fine_type=FineType.LATE_SUBMISSION,
            reason='Late submission',
            issued_by=admin_user
        )
        
        fine2 = FineService.issue_fine(
            order=order2,
            fine_type=FineType.LATE_SUBMISSION,
            reason='Late submission',
            issued_by=admin_user
        )
        
        assert fine1.amount == Decimal('25.00')
        assert fine2.amount == Decimal('25.00')
        assert fine1.status == FineStatus.ISSUED
        assert fine2.status == FineStatus.ISSUED

