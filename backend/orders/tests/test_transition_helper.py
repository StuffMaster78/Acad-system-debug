"""
Tests for OrderTransitionHelper and transition validation.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from orders.models import Order
from orders.services.transition_helper import (
    OrderTransitionHelper,
    InvalidTransitionError,
    AlreadyInTargetStatusError
)
from orders.exceptions import InvalidTransitionError as InvalidTransitionErrorException
from websites.models import Website
from order_configs.models import PaperType

User = get_user_model()


class OrderTransitionHelperTestCase(TestCase):
    """Test cases for OrderTransitionHelper."""
    
    def setUp(self):
        """Set up test data."""
        self.website = Website.objects.create(
            name='Test Website',
            domain='https://test.com',
            is_active=True
        )
        
        self.client_user = User.objects.create_user(
            username='testclient',
            email='client@test.com',
            role='client',
            website=self.website
        )
        
        self.writer_user = User.objects.create_user(
            username='testwriter',
            email='writer@test.com',
            role='writer',
            website=self.website
        )
        
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            role='admin',
            website=self.website,
            is_staff=True
        )
        
        self.paper_type = PaperType.objects.create(
            name='Essay',
            website=self.website
        )
        
        self.order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Test Order',
            paper_type=self.paper_type,
            number_of_pages=5,
            client_deadline=timezone.now() + timezone.timedelta(days=7),
            status='unpaid',
            is_paid=False
        )
    
    def test_valid_transition(self):
        """Test that valid transitions work."""
        # Transition from unpaid to paid
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason='Payment received',
            action='mark_paid'
        )
        
        self.assertEqual(updated_order.status, 'paid')
        self.assertEqual(updated_order.id, self.order.id)
    
    def test_invalid_transition_raises_error(self):
        """Test that invalid transitions raise InvalidTransitionError."""
        # Try to transition from unpaid directly to completed (invalid)
        with self.assertRaises(InvalidTransitionErrorException):
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='completed',
                user=self.admin_user,
                reason='Test'
            )
    
    def test_already_in_target_status(self):
        """Test that transitioning to current status raises error."""
        # Order is already in 'unpaid' status
        with self.assertRaises(AlreadyInTargetStatusError):
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='unpaid',
                user=self.admin_user,
                reason='Test'
            )
    
    def test_can_transition(self):
        """Test can_transition helper method."""
        # Should be able to transition from unpaid to paid
        self.assertTrue(
            OrderTransitionHelper.can_transition(self.order, 'paid')
        )
        
        # Should not be able to transition from unpaid to completed
        self.assertFalse(
            OrderTransitionHelper.can_transition(self.order, 'completed')
        )
        
        # Should not be able to transition to same status
        self.assertFalse(
            OrderTransitionHelper.can_transition(self.order, 'unpaid')
        )
    
    def test_get_available_transitions(self):
        """Test get_available_transitions helper method."""
        transitions = OrderTransitionHelper.get_available_transitions(self.order)
        
        # Unpaid orders can transition to: paid, cancelled, deleted, on_hold, pending, in_progress
        self.assertIn('paid', transitions)
        self.assertIn('cancelled', transitions)
        self.assertIn('on_hold', transitions)
        self.assertNotIn('completed', transitions)  # Can't go directly to completed
    
    def test_payment_validation(self):
        """Test payment validation for statuses requiring payment."""
        # Try to transition to in_progress without payment
        with self.assertRaises(ValidationError):
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='in_progress',
                user=self.admin_user,
                reason='Test'
            )
        
        # Should work with skip_payment_check (admin override)
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='in_progress',
            user=self.admin_user,
            reason='Admin override',
            skip_payment_check=True
        )
        self.assertEqual(updated_order.status, 'in_progress')
    
    def test_custom_validation_rules(self):
        """Test custom validation rules for specific transitions."""
        # Mark order as paid first
        self.order.is_paid = True
        self.order.status = 'paid'
        self.order.save()
        
        # Try to cancel paid order as non-admin (should fail)
        with self.assertRaises(ValidationError) as cm:
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='cancelled',
                user=self.client_user,  # Client, not admin
                reason='Want to cancel'
            )
        self.assertIn('Cannot cancel a paid order', str(cm.exception))
        
        # Should work as admin
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='cancelled',
            user=self.admin_user,  # Admin can cancel paid orders
            reason='Admin cancellation',
            skip_payment_check=True
        )
        self.assertEqual(updated_order.status, 'cancelled')
    
    def test_transition_logging(self):
        """Test that transitions are logged to OrderTransitionLog."""
        from orders.models import OrderTransitionLog
        
        initial_count = OrderTransitionLog.objects.count()
        
        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason='Payment received',
            action='mark_paid'
        )
        
        # Should have created a log entry
        self.assertEqual(OrderTransitionLog.objects.count(), initial_count + 1)
        
        log_entry = OrderTransitionLog.objects.latest('created_at')
        self.assertEqual(log_entry.order.id, self.order.id)
        self.assertEqual(log_entry.old_status, 'unpaid')
        self.assertEqual(log_entry.new_status, 'paid')
        self.assertEqual(log_entry.user, self.admin_user)
    
    def test_transition_hooks(self):
        """Test before/after transition hooks."""
        hook_called = {'before': False, 'after': False}
        
        def before_hook(order, user, metadata):
            hook_called['before'] = True
            self.assertEqual(order.id, self.order.id)
        
        def after_hook(order, user, metadata):
            hook_called['after'] = True
            self.assertEqual(order.status, 'paid')
        
        # Register hooks
        OrderTransitionHelper.register_before_hook('unpaid', 'paid', before_hook)
        OrderTransitionHelper.register_after_hook('unpaid', 'paid', after_hook)
        
        # Perform transition
        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason='Test hooks'
        )
        
        # Verify hooks were called
        self.assertTrue(hook_called['before'])
        self.assertTrue(hook_called['after'])

