"""
Edge case tests for order transitions.
Tests race conditions, concurrent transitions, and boundary conditions.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.db.models import F
import threading

from orders.models import Order, OrderTransitionLog
from orders.services.transition_helper import OrderTransitionHelper
from orders.exceptions import InvalidTransitionError, AlreadyInTargetStatusError
from websites.models import Website
from order_configs.models import PaperType

User = get_user_model()


class OrderTransitionEdgeCasesTestCase(TestCase):
    """Edge case tests for order transitions."""
    
    def setUp(self):
        """Set up test data."""
        self.website = Website.objects.create(
            name='Test Website',
            domain='https://test.com',
            is_active=True
        )
        
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            role='admin',
            website=self.website,
            is_staff=True
        )
        
        self.client_user = User.objects.create_user(
            username='testclient',
            email='client@test.com',
            role='client',
            website=self.website
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
    
    def test_concurrent_transitions_race_condition(self):
        """Test handling of concurrent transition attempts."""
        results = []
        errors = []
        
        def attempt_transition():
            try:
                # Refresh order to get latest state
                order = Order.objects.get(id=self.order.id)
                OrderTransitionHelper.transition_order(
                    order=order,
                    target_status='paid',
                    user=self.admin_user,
                    reason='Concurrent test'
                )
                results.append('success')
            except (InvalidTransitionError, AlreadyInTargetStatusError, ValidationError) as e:
                errors.append(str(e))
        
        # Attempt concurrent transitions
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=attempt_transition)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Only one should succeed, others should fail gracefully
        self.assertEqual(len(results), 1)
        self.assertGreaterEqual(len(errors), 4)  # At least 4 should fail
        
        # Verify order is in correct state
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
    
    def test_transition_to_same_status(self):
        """Test that transitioning to same status raises error."""
        self.order.status = 'paid'
        self.order.save()
        
        with self.assertRaises(AlreadyInTargetStatusError):
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='paid',
                user=self.admin_user,
                reason='Same status test'
            )
    
    def test_transition_with_nonexistent_status(self):
        """Test transition to a status that doesn't exist in VALID_TRANSITIONS."""
        with self.assertRaises(InvalidTransitionError):
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='nonexistent_status',
                user=self.admin_user,
                reason='Invalid status test'
            )
    
    def test_transition_with_empty_reason(self):
        """Test transition with empty reason (should still work)."""
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason=''
        )
        
        self.assertEqual(updated_order.status, 'paid')
        
        # Verify log entry has empty reason
        log_entry = OrderTransitionLog.objects.latest('created_at')
        self.assertEqual(log_entry.meta.get('reason'), '')
    
    def test_transition_with_very_long_reason(self):
        """Test transition with very long reason (should be truncated if needed)."""
        long_reason = 'A' * 1000  # Very long reason
        
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason=long_reason
        )
        
        self.assertEqual(updated_order.status, 'paid')
        
        # Verify log entry has reason (may be truncated by model)
        log_entry = OrderTransitionLog.objects.latest('created_at')
        self.assertIn('reason', log_entry.meta)
    
    def test_transition_with_complex_metadata(self):
        """Test transition with complex nested metadata."""
        complex_metadata = {
            'nested': {
                'level1': {
                    'level2': 'value'
                }
            },
            'array': [1, 2, 3],
            'boolean': True,
            'null_value': None
        }
        
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason='Complex metadata test',
            metadata=complex_metadata
        )
        
        self.assertEqual(updated_order.status, 'paid')
        
        # Verify metadata is preserved
        log_entry = OrderTransitionLog.objects.latest('created_at')
        self.assertIn('nested', log_entry.meta)
        self.assertEqual(log_entry.meta['nested']['level1']['level2'], 'value')
    
    def test_transition_with_failing_hook(self):
        """Test that failing hooks don't block transitions."""
        def failing_hook(order, user, metadata):
            raise Exception("Hook failed intentionally")
        
        OrderTransitionHelper.register_before_hook('unpaid', 'paid', failing_hook)
        
        # Transition should still succeed despite hook failure
        updated_order = OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason='Failing hook test'
        )
        
        self.assertEqual(updated_order.status, 'paid')
    
    def test_multiple_hooks_same_transition(self):
        """Test multiple hooks for the same transition."""
        hook_results = []
        
        def hook1(order, user, metadata):
            hook_results.append('hook1')
        
        def hook2(order, user, metadata):
            hook_results.append('hook2')
        
        def hook3(order, user, metadata):
            hook_results.append('hook3')
        
        OrderTransitionHelper.register_before_hook('unpaid', 'paid', hook1)
        OrderTransitionHelper.register_before_hook('unpaid', 'paid', hook2)
        OrderTransitionHelper.register_before_hook('unpaid', 'paid', hook3)
        
        OrderTransitionHelper.transition_order(
            order=self.order,
            target_status='paid',
            user=self.admin_user,
            reason='Multiple hooks test'
        )
        
        # All hooks should be called
        self.assertEqual(len(hook_results), 3)
        self.assertIn('hook1', hook_results)
        self.assertIn('hook2', hook_results)
        self.assertIn('hook3', hook_results)
    
    def test_transition_with_deleted_order(self):
        """Test transition behavior with soft-deleted order."""
        # Soft delete the order
        self.order.is_deleted = True
        self.order.deleted_at = timezone.now()
        self.order.save()
        
        # Transition should still work (OrderManager filters, but we can access via all_objects)
        # However, in practice, soft-deleted orders might be filtered out
        # This test verifies the system handles it gracefully
        order = Order.all_objects.get(id=self.order.id)
        
        # Transition should work if we access via all_objects
        updated_order = OrderTransitionHelper.transition_order(
            order=order,
            target_status='paid',
            user=self.admin_user,
            reason='Soft deleted order test'
        )
        
        self.assertEqual(updated_order.status, 'paid')
    
    def test_transition_chain(self):
        """Test multiple transitions in sequence."""
        # unpaid -> paid -> available -> in_progress
        order = self.order
        
        order = OrderTransitionHelper.transition_order(
            order=order,
            target_status='paid',
            user=self.admin_user,
            reason='Step 1'
        )
        self.assertEqual(order.status, 'paid')
        
        order = OrderTransitionHelper.transition_order(
            order=order,
            target_status='available',
            user=self.admin_user,
            reason='Step 2'
        )
        self.assertEqual(order.status, 'available')
        
        # Can't go directly to in_progress without writer assignment
        # But we can test the chain up to available
        
        # Verify all transitions were logged
        logs = OrderTransitionLog.objects.filter(order=self.order).order_by('created_at')
        self.assertGreaterEqual(logs.count(), 2)

