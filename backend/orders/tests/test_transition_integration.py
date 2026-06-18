"""
Integration tests for order transition system.
Tests the full flow from API endpoint to service layer.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from orders.models.orders import Order
from orders.models.orders.order_timeline_event import OrderTimelineEvent
from websites.models.websites import Website
from order_configs.models import PaperType

User = get_user_model()


class OrderTransitionIntegrationTestCase(TestCase):
    """Integration tests for order transitions via API and services."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.website, _ = Website.objects.get_or_create(
            domain='transition.test.local',
            defaults={
                'name': 'Transition Test Website',
                'is_active': True,
            },
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
            base_quantity=5,
            client_deadline=timezone.now() + timezone.timedelta(days=7),
            status='ready_for_staffing',
            total_price=Decimal("100.00"),
            amount_paid=Decimal("100.00"),
            payment_status="fully_paid",
        )

    def test_transition_api_endpoint_get(self):
        """Test GET endpoint for available transitions."""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(f'/api/v1/orders/orders/{self.order.id}/transition/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_transitions', response.data)
        self.assertIn('current_status', response.data)
        self.assertEqual(response.data['current_status'], 'ready_for_staffing')
        self.assertIn('in_progress', response.data['available_transitions'])

    def test_transition_api_endpoint_post_success(self):
        """Test POST endpoint for successful transition."""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'in_progress',
                'reason': 'Staff assigned the order'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('old_status', response.data)
        self.assertIn('new_status', response.data)
        self.assertEqual(response.data['old_status'], 'ready_for_staffing')
        self.assertEqual(response.data['new_status'], 'in_progress')

        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_transition_api_endpoint_post_invalid(self):
        """Test POST endpoint for invalid transition."""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'completed', # Invalid: can't go from unpaid to completed
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

    def test_client_cannot_use_generic_transition_endpoint(self):
        """Clients must use dedicated workflow actions, not generic transitions."""
        self.client.force_authenticate(user=self.client_user)

        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'in_progress',
                'reason': 'Unauthorized lifecycle change',
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_transition_logging_integration(self):
        """Test that transitions are logged via API."""
        initial_count = OrderTimelineEvent.objects.count()

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            f'/api/v1/orders/orders/{self.order.id}/transition/',
            {
                'target_status': 'in_progress',
                'reason': 'Staff assigned the order',
                'metadata': {'source': 'api_test'}
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify log entry was created
        self.assertEqual(OrderTimelineEvent.objects.count(), initial_count + 1)

        log_entry = OrderTimelineEvent.objects.latest('created_at')
        self.assertEqual(log_entry.order.id, self.order.id)
        self.assertEqual(
            log_entry.metadata["from_status"],
            "ready_for_staffing",
        )
        self.assertEqual(log_entry.metadata["to_status"], "in_progress")
        self.assertEqual(log_entry.actor, self.admin_user)

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
                'target_status': 'in_progress',
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
                'target_status': 'in_progress',
                'reason': 'Test metadata',
                'metadata': custom_metadata
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify metadata in log
        log_entry = OrderTimelineEvent.objects.latest('created_at')
        self.assertIn('source', log_entry.metadata)
        self.assertEqual(log_entry.metadata.get('source'), 'api_test')
        self.assertEqual(log_entry.metadata.get('test_id'), '12345')
