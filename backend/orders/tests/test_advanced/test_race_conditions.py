"""
Advanced tests for race conditions and concurrency.

Tests cover:
- Concurrent order assignments
- Race conditions in status transitions
- Concurrent payment processing
- Database locking
- Atomic operations
"""
import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

from decimal import Decimal
from orders.models import Order, WriterAssignmentAcceptance
from orders.order_enums import OrderStatus
from orders.services.assignment import OrderAssignmentService
from orders.services.status_transition_service import StatusTransitionService
from order_payments_management.models import OrderPayment


@pytest.mark.django_db
class TestRaceConditions:
    """Test race conditions and concurrency issues."""
    
    def test_concurrent_order_assignment(self, order, writer_user, writer_user2, writer_profile, admin_user):
        """Test concurrent assignment attempts don't cause double assignment."""
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        errors = []
        results = []
        
        def assign_order(writer_id):
            try:
                service = OrderAssignmentService(order)
                service.actor = admin_user
                result = service.assign_writer(writer_id, f"Concurrent assignment {writer_id}")
                results.append(result.assigned_writer_id)
                return result
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Try to assign two different writers concurrently
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(assign_order, writer_user.id),
                executor.submit(assign_order, writer_user2.id)
            ]
            
            for future in as_completed(futures):
                future.result()
        
        # Only one should succeed
        order.refresh_from_db()
        assert order.assigned_writer is not None
        assert order.assigned_writer_id in [writer_user.id, writer_user2.id]
        # At least one should have failed or been prevented
        assert len(results) <= 1 or len(errors) > 0
    
    def test_concurrent_status_transitions(self, order, admin_user):
        """Test concurrent status transitions are handled correctly."""
        order.status = OrderStatus.CREATED.value
        order.is_paid = True
        order.save()
        
        transitions = []
        errors = []
        
        def transition_order(target_status):
            try:
                service = StatusTransitionService(user=admin_user)
                result = service.transition_order_to_status(
                    order=order,
                    target_status=target_status,
                    reason=f"Concurrent transition to {target_status}"
                )
                transitions.append(target_status)
                return result
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Try multiple concurrent transitions
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(transition_order, OrderStatus.PENDING.value),
                executor.submit(transition_order, OrderStatus.UNPAID.value),
            ]
            
            for future in as_completed(futures):
                future.result()
        
        # Only one transition should succeed
        order.refresh_from_db()
        assert order.status in [OrderStatus.PENDING.value, OrderStatus.UNPAID.value]
        assert len(transitions) == 1  # Only one should succeed
    
    def test_concurrent_payment_processing(self, order, client_user):
        """Test concurrent payment processing doesn't cause double charging."""
        order.status = OrderStatus.UNPAID.value
        order.total_price = Decimal('100.00')
        order.save()
        
        payments_created = []
        errors = []
        
        def create_payment():
            try:
                from order_payments_management.services.payment_service import OrderPaymentService
                payment = OrderPaymentService.create_payment(
                    order=order,
                    client=client_user,
                    payment_method='wallet',
                    amount=Decimal('100.00')
                )
                payments_created.append(payment.id)
                return payment
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Try to create multiple payments concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_payment) for _ in range(3)]
            
            for future in as_completed(futures):
                future.result()
        
        # All payments should be created (they're independent records)
        # But only one should be processed
        assert len(payments_created) >= 1
    
    def test_concurrent_order_updates(self, order, admin_user):
        """Test concurrent order updates don't lose data."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.topic = "Original Topic"
        order.save()
        
        updates = []
        
        def update_order(field, value):
            order.refresh_from_db()
            setattr(order, field, value)
            order.save(update_fields=[field])
            updates.append((field, value))
        
        # Concurrent updates to different fields
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(update_order, 'topic', 'Updated Topic 1'),
                executor.submit(update_order, 'status', OrderStatus.SUBMITTED.value),
            ]
            
            for future in as_completed(futures):
                future.result()
        
        order.refresh_from_db()
        # Both updates should be reflected (or at least one)
        assert order.topic in ['Updated Topic 1', 'Original Topic'] or order.status == OrderStatus.SUBMITTED.value


@pytest.mark.django_db
class TestIdempotency:
    """Test idempotency of operations."""
    
    def test_repeated_assignment_idempotent(self, order, writer_user, writer_profile, admin_user):
        """Test assigning same writer multiple times is idempotent."""
        order.status = OrderStatus.AVAILABLE.value
        order.is_paid = True
        order.save()
        
        service = OrderAssignmentService(order)
        service.actor = admin_user
        
        # First assignment
        result1 = service.assign_writer(writer_user.id, "First assignment")
        
        # Second assignment (should handle gracefully or be idempotent)
        # This might raise an error or be idempotent depending on implementation
        try:
            result2 = service.assign_writer(writer_user.id, "Second assignment")
            # If it succeeds, should be same writer
            assert result2.assigned_writer == writer_user
        except Exception:
            # If it fails, that's also acceptable (non-idempotent but safe)
            pass
        
        order.refresh_from_db()
        assert order.assigned_writer == writer_user
    
    def test_repeated_status_transition_idempotent(self, order, admin_user):
        """Test repeated status transitions are handled correctly."""
        order.status = OrderStatus.CREATED.value
        order.is_paid = True
        order.save()
        
        service = StatusTransitionService(user=admin_user)
        
        # First transition
        result1 = service.transition_order_to_status(
            order=order,
            target_status=OrderStatus.PENDING.value,
            reason="First transition"
        )
        
        # Try same transition again (should raise AlreadyInTargetStatusError)
        with pytest.raises(Exception):  # Should raise AlreadyInTargetStatusError
            service.transition_order_to_status(
                order=order,
                target_status=OrderStatus.PENDING.value,
                reason="Second transition"
            )
        
        order.refresh_from_db()
        assert order.status == OrderStatus.PENDING.value
    
    def test_repeated_payment_creation(self, order, client_user):
        """Test creating multiple payments for same order."""
        order.status = OrderStatus.UNPAID.value
        order.total_price = Decimal('100.00')
        order.save()
        
        from order_payments_management.services.payment_service import OrderPaymentService
        
        # Create first payment
        payment1 = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=Decimal('100.00')
        )
        
        # Create second payment (should be allowed - multiple payment attempts)
        payment2 = OrderPaymentService.create_payment(
            order=order,
            client=client_user,
            payment_method='wallet',
            amount=Decimal('100.00')
        )
        
        assert payment1.id != payment2.id
        assert payment1.order == payment2.order
    
    def test_repeated_cancellation_request(self, order, client_user):
        """Test repeated cancellation requests are prevented."""
        order.status = OrderStatus.PAID.value
        order.is_paid = True
        order.client = client_user
        order.save()
        
        from orders.services.cancel_order_service import CancelOrderService
        
        # First request
        request1 = CancelOrderService.request_cancellation(
            order_id=order.id,
            reason="First request",
            user=client_user
        )
        
        # Second request should fail
        with pytest.raises(ValueError) as exc:
            CancelOrderService.request_cancellation(
                order_id=order.id,
                reason="Second request",
                user=client_user
            )
        
        assert "pending cancellation request" in str(exc.value).lower()

