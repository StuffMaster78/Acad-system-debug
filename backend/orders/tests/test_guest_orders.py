"""
Tests for Guest Order endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from websites.models import Website, GuestAccessToken
from client_management.models import ClientProfile
from orders.models import Order

User = get_user_model()


class GuestOrderTestCase(TestCase):
    """Test cases for Guest Order endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.website = Website.objects.create(
            name='Test Website',
            domain='https://test.com',
            is_active=True,
            allow_guest_checkout=True,
            guest_requires_email_verification=True,
            guest_max_order_amount=200.00,
            guest_block_urgent_before_hours=12
        )
    
    def test_start_guest_order_creates_user_and_profile(self):
        """Test that starting a guest order creates user and client profile."""
        from order_configs.models import PaperType
        
        # Create required paper type
        paper_type = PaperType.objects.create(
            name='Essay',
            website=self.website
        )
        
        deadline = (timezone.now() + timedelta(days=2)).isoformat()
        
        response = self.client.post('/api/v1/orders/guest-orders/start/', {
            'website_id': self.website.id,
            'email': 'guest@example.com',
            'order_data': {
                'topic': 'Test Topic',
                'paper_type_id': paper_type.id,
                'number_of_pages': 5,
                'client_deadline': deadline,
                'order_instructions': 'Test instructions'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('verification_required'))
        
        # Check that user was created
        user = User.objects.get(email='guest@example.com')
        self.assertEqual(user.role, 'client')
        
        # Check that client profile was created
        profile = ClientProfile.objects.get(user=user, website=self.website)
        self.assertTrue(profile.is_guest)
    
    def test_start_guest_order_without_verification(self):
        """Test guest order creation when verification is not required."""
        from order_configs.models import PaperType
        
        self.website.guest_requires_email_verification = False
        self.website.save()
        
        paper_type = PaperType.objects.create(
            name='Essay',
            website=self.website
        )
        
        deadline = (timezone.now() + timedelta(days=2)).isoformat()
        
        response = self.client.post('/api/v1/orders/guest-orders/start/', {
            'website_id': self.website.id,
            'email': 'guest2@example.com',
            'order_data': {
                'topic': 'Test Topic',
                'paper_type_id': paper_type.id,
                'number_of_pages': 5,
                'client_deadline': deadline,
                'order_instructions': 'Test instructions'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data.get('verification_required'))
        self.assertIn('order_id', response.data)
        
        # Check that order was created
        order = Order.objects.get(id=response.data['order_id'])
        self.assertEqual(order.topic, 'Test Topic')
    
    def test_verify_email_creates_order(self):
        """Test that verifying email creates the order."""
        from order_configs.models import PaperType
        from hashlib import sha256
        from django.utils.crypto import get_random_string
        
        # Create user and token
        user = User.objects.create_user(
            email='verify@example.com',
            username='verify@example.com',
            role='client'
        )
        ClientProfile.objects.create(
            user=user,
            website=self.website,
            is_guest=True
        )
        
        verification_token = get_random_string(64)
        token_hash = sha256(verification_token.encode()).hexdigest()
        
        GuestAccessToken.objects.create(
            website=self.website,
            user=user,
            token_hash=token_hash,
            scope=GuestAccessToken.SCOPE_ORDER,
            expires_at=timezone.now() + timedelta(hours=72)
        )
        
        paper_type = PaperType.objects.create(
            name='Essay',
            website=self.website
        )
        
        deadline = (timezone.now() + timedelta(days=2)).isoformat()
        
        response = self.client.post('/api/v1/orders/guest-orders/verify-email/', {
            'verification_token': verification_token,
            'website_id': self.website.id,
            'order_data': {
                'topic': 'Verified Order',
                'paper_type_id': paper_type.id,
                'number_of_pages': 3,
                'client_deadline': deadline,
                'order_instructions': 'Verified instructions'
            }
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_id', response.data)
        
        # Check that order was created
        order = Order.objects.get(id=response.data['order_id'])
        self.assertEqual(order.topic, 'Verified Order')
        self.assertEqual(order.client, user)
        
        # Check that token was marked as used
        token = GuestAccessToken.objects.get(token_hash=token_hash)
        self.assertIsNotNone(token.used_at)

