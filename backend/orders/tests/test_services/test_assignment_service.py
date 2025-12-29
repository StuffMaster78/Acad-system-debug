"""
Comprehensive tests for OrderAssignmentService.

Tests cover:
- Writer assignment
- Writer unassignment
- Reassignment scenarios
- Permission checks
- Workload limits
- Admin overrides
- Notifications
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, WriterAssignmentAcceptance, WriterReassignmentLog
from orders.order_enums import OrderStatus
from orders.services.assignment import OrderAssignmentService
from writer_management.models import WriterProfile, WriterLevel


@pytest.mark.django_db
class TestOrderAssignmentService:
    """Test OrderAssignmentService functionality."""
    
    def test_assign_writer_success(self, order, writer_user, writer_profile):
        """Test successful writer assignment."""
        # Ensure order is in assignable state
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        service.actor = None  # No actor for basic assignment
        
        result = service.assign_writer(
            writer_id=writer_user.id,
            reason="Test assignment"
        )
        
        assert result.assigned_writer == writer_user
        assert result.status == OrderStatus.PENDING_WRITER_ASSIGNMENT.value
        
        # Check assignment acceptance was created
        acceptance = WriterAssignmentAcceptance.objects.get(order=order)
        assert acceptance.writer == writer_user
        assert acceptance.status == 'pending'
    
    def test_assign_writer_with_payment_amount(self, order, writer_user, writer_profile):
        """Test assignment with custom payment amount."""
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        custom_amount = Decimal('150.00')
        
        result = service.assign_writer(
            writer_id=writer_user.id,
            reason="Test assignment with custom payment",
            writer_payment_amount=custom_amount
        )
        
        assert result.writer_compensation == custom_amount
    
    def test_assign_writer_invalid_writer_id(self, order):
        """Test assignment with non-existent writer."""
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        
        with pytest.raises(ObjectDoesNotExist):
            service.assign_writer(
                writer_id=99999,
                reason="Test assignment"
            )
    
    def test_assign_writer_inactive_writer(self, order, writer_user):
        """Test assignment with inactive writer."""
        writer_user.is_active = False
        writer_user.save()
        
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        
        with pytest.raises(ObjectDoesNotExist):
            service.assign_writer(
                writer_id=writer_user.id,
                reason="Test assignment"
            )
    
    def test_assign_writer_already_assigned(self, order, writer_user, writer_profile, admin_user):
        """Test assignment when order already has a writer."""
        # Assign first writer
        order.assigned_writer = writer_user
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        # Try to assign another writer (non-admin)
        service = OrderAssignmentService(order)
        service.actor = None  # Regular user
        
        with pytest.raises(ValidationError) as exc:
            service.assign_writer(
                writer_id=writer_user.id,
                reason="Reassignment attempt"
            )
        
        assert "already assigned" in str(exc.value).lower()
    
    def test_assign_writer_admin_reassignment(self, order, writer_user, writer_profile, admin_user, writer_user2):
        """Test admin can reassign orders."""
        # Assign first writer
        order.assigned_writer = writer_user
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        # Admin reassigns to another writer
        service = OrderAssignmentService(order)
        service.actor = admin_user
        
        result = service.assign_writer(
            writer_id=writer_user2.id,
            reason="Admin reassignment"
        )
        
        assert result.assigned_writer == writer_user2
        
        # Check reassignment log was created
        reassignment = WriterReassignmentLog.objects.filter(order=order).first()
        assert reassignment is not None
        assert reassignment.previous_writer == writer_user
        assert reassignment.new_writer == writer_user2
    
    def test_assign_writer_workload_limit(self, order, writer_user, writer_profile, writer_level):
        """Test assignment fails when writer reaches workload limit."""
        # Set low max orders
        writer_level.max_orders = 2
        writer_level.save()
        
        writer_profile.writer_level = writer_level
        writer_profile.save()
        
        # Create 2 active orders for this writer
        from orders.models import Order as OrderModel
        for i in range(2):
            OrderModel.objects.create(
                client=order.client,
                website=order.website,
                assigned_writer=writer_user,
                status=OrderStatus.IN_PROGRESS.value,
                topic=f"Test Order {i}",
                client_deadline=timezone.now() + timedelta(days=1),
                is_paid=True
            )
        
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        
        with pytest.raises(ValidationError) as exc:
            service.assign_writer(
                writer_id=writer_user.id,
                reason="Test assignment"
            )
        
        assert "maximum order limit" in str(exc.value).lower()
    
    def test_assign_writer_admin_overrides_workload(self, order, writer_user, writer_profile, writer_level, admin_user):
        """Test admin can override workload limits."""
        # Set low max orders
        writer_level.max_orders = 1
        writer_level.save()
        
        writer_profile.writer_level = writer_level
        writer_profile.save()
        
        # Create 1 active order
        from orders.models import Order as OrderModel
        OrderModel.objects.create(
            client=order.client,
            website=order.website,
            assigned_writer=writer_user,
            status=OrderStatus.IN_PROGRESS.value,
            topic="Existing Order",
            client_deadline=timezone.now() + timedelta(days=1),
            is_paid=True
        )
        
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        # Admin can override
        service = OrderAssignmentService(order)
        service.actor = admin_user
        
        result = service.assign_writer(
            writer_id=writer_user.id,
            reason="Admin override"
        )
        
        assert result.assigned_writer == writer_user
    
    def test_unassign_writer_success(self, order, writer_user):
        """Test successful writer unassignment."""
        order.assigned_writer = writer_user
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        service = OrderAssignmentService(order)
        service.actor = None
        
        result = service.unassign_writer()
        
        assert result.assigned_writer is None
        assert result.status == OrderStatus.AVAILABLE.value
    
    def test_unassign_writer_not_assigned(self, order):
        """Test unassignment when no writer is assigned."""
        order.assigned_writer = None
        order.save()
        
        service = OrderAssignmentService(order)
        
        with pytest.raises(ValidationError) as exc:
            service.unassign_writer()
        
        assert "not currently assigned" in str(exc.value).lower()
    
    def test_assign_writer_writer_level_too_low(self, order, writer_user, writer_profile, writer_level):
        """Test assignment fails when writer level is too low."""
        # Set writer level to low
        writer_level.level_number = 1
        writer_level.save()
        
        writer_profile.writer_level = writer_level
        writer_profile.save()
        
        # Set order to require higher level
        order.academic_level = "PhD"  # Typically requires higher level
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        
        # Mock OrderAccessService to return False
        with pytest.raises(PermissionDenied) as exc:
            service.assign_writer(
                writer_id=writer_user.id,
                reason="Test assignment"
            )
        
        assert "level too low" in str(exc.value).lower() or "cannot be assigned" in str(exc.value).lower()
    
    def test_reassignment_updates_old_acceptance(self, order, writer_user, writer_user2, writer_profile, admin_user):
        """Test reassignment updates old acceptance record."""
        # Initial assignment
        order.assigned_writer = writer_user
        order.status = OrderStatus.PENDING_WRITER_ASSIGNMENT.value
        order.save()
        
        # Create pending acceptance
        WriterAssignmentAcceptance.objects.create(
            order=order,
            writer=writer_user,
            status='pending',
            website=order.website
        )
        
        # Reassign
        service = OrderAssignmentService(order)
        service.actor = admin_user
        
        result = service.assign_writer(
            writer_id=writer_user2.id,
            reason="Reassignment"
        )
        
        # Check old acceptance was rejected
        old_acceptance = WriterAssignmentAcceptance.objects.get(
            order=order,
            writer=writer_user
        )
        assert old_acceptance.status == 'rejected'
        assert "Reassigned" in old_acceptance.reason
        
        # Check new acceptance was created
        new_acceptance = WriterAssignmentAcceptance.objects.get(
            order=order,
            writer=writer_user2
        )
        assert new_acceptance.status == 'pending'


@pytest.mark.django_db
class TestOrderAssignmentServiceReassignment:
    """Test reassignment scenarios."""
    
    def test_reassignment_from_in_progress(self, order, writer_user, writer_user2, writer_profile, admin_user):
        """Test reassigning from in_progress status."""
        order.assigned_writer = writer_user
        order.status = OrderStatus.IN_PROGRESS.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        service.actor = admin_user
        
        result = service.assign_writer(
            writer_id=writer_user2.id,
            reason="Reassignment from in_progress"
        )
        
        assert result.assigned_writer == writer_user2
        assert result.status == OrderStatus.REASSIGNED.value
    
    def test_reassignment_creates_log(self, order, writer_user, writer_user2, writer_profile, admin_user):
        """Test reassignment creates log entry."""
        order.assigned_writer = writer_user
        order.status = OrderStatus.IN_PROGRESS.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        service.actor = admin_user
        
        service.assign_writer(
            writer_id=writer_user2.id,
            reason="Reassignment test"
        )
        
        log = WriterReassignmentLog.objects.filter(order=order).first()
        assert log is not None
        assert log.previous_writer == writer_user
        assert log.new_writer == writer_user2
        assert log.reassigned_by == admin_user


@pytest.fixture
def writer_user2(website):
    """Create a second test writer."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username="test_writer2",
        email="writer2@test.com",
        password="testpass123",
        role="writer",
        website=website,
        is_active=True
    )


# Note: writer_profile and writer_level fixtures are defined in conftest.py

