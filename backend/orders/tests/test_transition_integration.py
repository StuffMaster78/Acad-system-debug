"""
Integration tests for order transition system.
Tests the full flow from API endpoint to service layer.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from orders.models import Order, OrderTransitionLog
from orders.services.transition_helper import OrderTransitionHelper
from websites.models import Website
from order_configs.models import PaperType

User = get_user_model()


class OrderTransitionIntegrationTestCase(TestCase):
    """Integration tests for order transitions via API and services."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
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
    
    def test_transition_api_endpoint_get(self):
        """Test GET endpoint for available transitions."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/v1/orders/orders/{self.order.id}/transition/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_transitions', response.data)
        self.assertIn('current_status', response.data)
        self.assertEqual(response.data['current_status'], 'unpaid')
        self.assertIn('paid', response.data['available_transitions'])
    
    def test_transition_api_endpoint_post_success(self):
        """Test POST endpoint for successful transition."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'paid',
                'reason': 'Payment received via test'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('old_status', response.data)
        self.assertIn('new_status', response.data)
        self.assertEqual(response.data['old_status'], 'unpaid')
        self.assertEqual(response.data['new_status'], 'paid')
        
        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
    
    def test_transition_api_endpoint_post_invalid(self):
        """Test POST endpoint for invalid transition."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'completed',  # Invalid: can't go from unpaid to completed
                'reason': 'Test invalid transition'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
    
    def test_transition_api_endpoint_post_missing_status(self):
        """Test POST endpoint with missing target_status."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'reason': 'Test missing status'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_status is required', response.data['detail'])
    
    def test_transition_with_custom_validation(self):
        """Test transition with custom validation rules."""
        # Mark order as paid
        self.order.is_paid = True
        self.order.status = 'paid'
        self.order.save()
        
        self.client.force_authenticate(user=self.client_user)  # Non-admin
        
        # Try to cancel paid order as non-admin (should fail)
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'cancelled',
                'reason': 'Want to cancel'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Cannot cancel a paid order', response.data['detail'])
        
        # Should work as admin
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'cancelled',
                'reason': 'Admin cancellation',
                'skip_payment_check': True
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_transition_logging_integration(self):
        """Test that transitions are logged via API."""
        initial_count = OrderTransitionLog.objects.count()
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'paid',
                'reason': 'Payment received',
                'metadata': {'source': 'api_test'}
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify log entry was created
        self.assertEqual(OrderTransitionLog.objects.count(), initial_count + 1)
        
        log_entry = OrderTransitionLog.objects.latest('created_at')
        self.assertEqual(log_entry.order.id, self.order.id)
        self.assertEqual(log_entry.old_status, 'unpaid')
        self.assertEqual(log_entry.new_status, 'paid')
        self.assertEqual(log_entry.user, self.admin_user)
    
    def test_transition_hooks_integration(self):
        """Test that hooks are executed during API transitions."""
        hook_called = {'before': False, 'after': False}
        
        def before_hook(order, user, metadata):
            hook_called['before'] = True
        
        def after_hook(order, user, metadata):
            hook_called['after'] = True
        
        # Register hooks
        OrderTransitionHelper.register_before_hook('unpaid', 'paid', before_hook)
        OrderTransitionHelper.register_after_hook('unpaid', 'paid', after_hook)
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'paid',
                'reason': 'Test hooks'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(hook_called['before'])
        self.assertTrue(hook_called['after'])
    
    def test_transition_permission_check(self):
        """Test that transitions respect permissions."""
        # Client should not be able to transition orders they don't own
        other_client = User.objects.create_user(
            username='otherclient',
            email='other@test.com',
            role='client',
            website=self.website
        )
        
        self.client.force_authenticate(user=other_client)
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'paid',
                'reason': 'Unauthorized attempt'
            }
        )
        
        # Should fail with permission error (403 or 404)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_transition_metadata_preservation(self):
        """Test that metadata is preserved through transition."""
        self.client.force_authenticate(user=self.admin_user)
        
        custom_metadata = {
            'source': 'api_test',
            'test_id': '12345',
            'custom_field': 'custom_value'
        }
        
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'paid',
                'reason': 'Test metadata',
                'metadata': custom_metadata
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify metadata in log
        log_entry = OrderTransitionLog.objects.latest('created_at')
        self.assertIn('source', log_entry.meta)
        self.assertEqual(log_entry.meta.get('source'), 'api_test')
        self.assertEqual(log_entry.meta.get('test_id'), '12345')

