"""
Comprehensive tests for StatusTransitionService.

Tests cover:
- Valid status transitions
- Invalid transitions
- Payment validation
- Writer assignment validation
- Batch operations
- Edge cases
"""
import pytest
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Order, OrderTransitionLog
from orders.order_enums import OrderStatus
from orders.services.status_transition_service import StatusTransitionService, VALID_TRANSITIONS
from orders.exceptions import InvalidTransitionError, AlreadyInTargetStatusError


@pytest.mark.django_db
class TestStatusTransitionService:
    """Test StatusTransitionService functionality."""
    
    def test_transition_valid_status(self, order, admin_user):
        """Test valid status transition."""
        order.status = OrderStatus.CREATED.value
        order.is_paid = True
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        result = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.PENDING.value,
            reason="Test transition"
        )
        
        assert result.status == OrderStatus.PENDING.value
        
        # Check transition log was created
        log = OrderTransitionLog.objects.filter(order=order).first()
        assert log is not None
        assert log.old_status == OrderStatus.CREATED.value
        assert log.new_status == OrderStatus.PENDING.value
    
    def test_transition_invalid_status(self, order, admin_user):
        """Test invalid status transition raises error."""
        order.status = OrderStatus.CREATED.value
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        with pytest.raises(InvalidTransitionError) as exc:
            service.transition_order_to_status(
                order=order,
                target_status=OrderStatus.COMPLETED.value,  # Cannot go directly from CREATED to COMPLETED
                reason="Invalid transition"
            )
        
        assert "Cannot move from" in str(exc.value)
    
    def test_transition_already_in_target_status(self, order, admin_user):
        """Test transition when already in target status."""
        order.status = OrderStatus.PENDING.value
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        with pytest.raises(AlreadyInTargetStatusError) as exc:
            service.transition_order_to_status(
                order=order,
                target_status=OrderStatus.PENDING.value,
                reason="Already in status"
            )
        
        assert "already in status" in str(exc.value).lower()
    
    def test_transition_requires_payment(self, order, admin_user):
        """Test transition requires payment for certain statuses."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        with pytest.raises(ValidationError) as exc:
            service.transition_order_to_status(
                order=order,
                target_status=OrderStatus.IN_PROGRESS.value,
                reason="Needs payment"
            )
        
        assert "payment" in str(exc.value).lower()
    
    def test_transition_skip_payment_check(self, order, admin_user):
        """Test admin can skip payment check."""
        order.status = OrderStatus.UNPAID.value
        order.is_paid = False
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        result = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.IN_PROGRESS.value,
            skip_payment_check=True,
            reason="Admin override"
        )
        
        assert result.status == OrderStatus.IN_PROGRESS.value
    
    def test_transition_requires_writer(self, order, admin_user):
        """Test transition requires writer assignment for certain statuses."""
        order.status = OrderStatus.AVAILABLE.value
        order.assigned_writer = None
        order.is_paid = True
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        with pytest.raises(ValidationError) as exc:
            service.transition_order_to_status(
                order=order,
                target_status=OrderStatus.IN_PROGRESS.value,
                reason="Needs writer"
            )
        
        assert "assigned writer" in str(exc.value).lower()
    
    def test_get_available_transitions(self, order):
        """Test getting available transitions for an order."""
        order.status = OrderStatus.CREATED.value
        order.save()
        
        service = StatusTransitionService()
        transitions = service.get_available_transitions(order)
        
        assert isinstance(transitions, list)
        assert OrderStatus.PENDING.value in transitions
        assert OrderStatus.UNPAID.value in transitions
        assert OrderStatus.CANCELLED.value in transitions
    
    def test_transition_with_metadata(self, order, admin_user):
        """Test transition with metadata."""
        order.status = OrderStatus.CREATED.value
        order.is_paid = True
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        metadata = {
            "action": "manual_transition",
            "is_automatic": False,
            "custom_field": "test_value"
        }
        
        result = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.PENDING.value,
            metadata=metadata,
            reason="Test with metadata"
        )
        
        log = OrderTransitionLog.objects.filter(order=order).first()
        assert log.meta["custom_field"] == "test_value"
        assert log.meta["action"] == "manual_transition"
    
    def test_transition_without_logging(self, order, admin_user):
        """Test transition without audit logging."""
        order.status = OrderStatus.CREATED.value
        order.is_paid = True
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        result = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.PENDING.value,
            log_action=False,
            reason="No logging"
        )
        
        # Transition log should still be created (for OrderTransitionLog)
        log = OrderTransitionLog.objects.filter(order=order).first()
        assert log is not None  # OrderTransitionLog is always created


@pytest.mark.django_db
class TestStatusTransitionServiceBatchOperations:
    """Test batch status transition operations."""
    
    def test_move_complete_orders_to_approved(self, order, client_user, website):
        """Test batch moving complete orders to approved."""
        from orders.models import Order as OrderModel
        
        # Create orders in 'complete' status
        cutoff_date = timezone.now() - timedelta(days=1)
        
        old_order = OrderModel.objects.create(
            client=client_user,
            website=website,
            status=OrderStatus.COMPLETED.value,
            topic="Old Complete Order",
            client_deadline=cutoff_date - timedelta(days=1),
            is_paid=True
        )
        
        new_order = OrderModel.objects.create(
            client=client_user,
            website=website,
            status=OrderStatus.COMPLETED.value,
            topic="New Complete Order",
            client_deadline=timezone.now() + timedelta(days=1),
            is_paid=True
        )
        
        StatusTransitionService.move_complete_orders_to_approved_older_than(cutoff_date)
        
        old_order.refresh_from_db()
        new_order.refresh_from_db()
        
        assert old_order.status == OrderStatus.APPROVED.value
        assert new_order.status == OrderStatus.COMPLETED.value  # Not old enough
    
    def test_reopen_cancelled_order(self, order, client_user):
        """Test reopening a cancelled order."""
        order.status = OrderStatus.CANCELLED.value
        order.save()
        
        result = StatusTransitionService.reopen_cancelled_order_to_unpaid(order.id)
        
        assert result is not None
        assert result.status == OrderStatus.UNPAID.value
    
    def test_reopen_cancelled_order_not_found(self):
        """Test reopening non-existent cancelled order."""
        result = StatusTransitionService.reopen_cancelled_order_to_unpaid(99999)
        assert result is None
    
    def test_reopen_non_cancelled_order(self, order):
        """Test reopening order that's not cancelled."""
        order.status = OrderStatus.PENDING.value
        order.save()
        
        result = StatusTransitionService.reopen_cancelled_order_to_unpaid(order.id)
        assert result is None


@pytest.mark.django_db
class TestStatusTransitionServicePaymentValidation:
    """Test payment validation in transitions."""
    
    def test_transition_to_in_progress_requires_payment(self, order, admin_user, writer_user):
        """Test transitioning to in_progress requires payment."""
        order.status = OrderStatus.AVAILABLE.value
        order.assigned_writer = writer_user
        order.is_paid = False
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        with pytest.raises(ValidationError) as exc:
            service.transition_order_to_status(
                order=order,
                target_status=OrderStatus.IN_PROGRESS.value,
                reason="Needs payment"
            )
        
        assert "payment" in str(exc.value).lower()
    
    def test_transition_with_completed_payment(self, order, admin_user, writer_user):
        """Test transition works with completed payment."""
        from order_payments_management.models import OrderPayment
        
        order.status = OrderStatus.AVAILABLE.value
        order.assigned_writer = writer_user
        order.is_paid = False
        order.save()
        
        # Create completed payment
        OrderPayment.objects.create(
            order=order,
            amount=order.total_price or 100.00,
            status='completed',
            payment_method='wallet'
        )
        
        service = StatusTransitionService(user=admin_user)
        
        result = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.IN_PROGRESS.value,
            reason="Has payment"
        )
        
        assert result.status == OrderStatus.IN_PROGRESS.value


@pytest.mark.django_db
class TestStatusTransitionServiceEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_transition_from_final_state(self, order, admin_user):
        """Test transition from final state (should be limited)."""
        order.status = OrderStatus.ARCHIVED.value
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        # Archived can only go to closed
        transitions = service.get_available_transitions(order)
        assert OrderStatus.CLOSED.value in transitions
        assert len(transitions) == 1
    
    def test_transition_to_deleted_state(self, order, admin_user):
        """Test transition to deleted state (final state)."""
        order.status = OrderStatus.CANCELLED.value
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        # Deleted has no transitions
        transitions = service.get_available_transitions(order)
        # Cancelled can transition to reopened, unpaid, or refunded
        assert OrderStatus.REOPENED.value in transitions or OrderStatus.UNPAID.value in transitions
    
    def test_transition_without_user(self, order):
        """Test transition without user (still works, no audit log)."""
        order.status = OrderStatus.CREATED.value
        order.is_paid = True
        order.save()
        
        service = StatusTransitionService(user=None)
        
        result = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.PENDING.value,
            reason="No user"
        )
        
        assert result.status == OrderStatus.PENDING.value
        
        # Transition log should still be created
        log = OrderTransitionLog.objects.filter(order=order).first()
        assert log is not None
        assert log.user is None

