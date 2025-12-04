"""
Tests for SEO Pages endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from websites.models import Website

from .models import SeoPage

User = get_user_model()


class SeoPageAPITestCase(TestCase):
    """Test cases for SEO Pages API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='admin',
            is_staff=True
        )
        self.website = Website.objects.create(
            name='Test Website',
            domain='https://test.com',
            is_active=True
        )
        self.seo_page = SeoPage.objects.create(
            website=self.website,
            title='Test SEO Page',
            slug='test-seo-page',
            meta_title='Test Meta Title',
            meta_description='Test meta description',
            blocks=[{'type': 'paragraph', 'content': 'Test content'}],
            is_published=True,
            created_by=self.user
        )
    
    def test_list_seo_pages_requires_auth(self):
        """Test that listing SEO pages requires authentication."""
        response = self.client.get('/api/v1/seo-pages/seo-pages/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_seo_pages_authenticated(self):
        """Test listing SEO pages when authenticated."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/seo-pages/seo-pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_create_seo_page(self):
        """Test creating a new SEO page."""
        self.client.force_authenticate(user=self.user)
        data = {
            'website': self.website.id,
            'title': 'New SEO Page',
            'slug': 'new-seo-page',
            'meta_title': 'New Meta Title',
            'meta_description': 'New meta description',
            'blocks': [{'type': 'heading', 'content': 'Heading'}],
            'is_published': False
        }
        response = self.client.post('/api/v1/seo-pages/seo-pages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SeoPage.objects.count(), 2)
    
    def test_public_get_seo_page_by_slug(self):
        """Test public endpoint to get SEO page by slug."""
        response = self.client.get(f'/api/v1/public/seo-pages/{self.seo_page.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.seo_page.title)
        self.assertEqual(response.data['slug'], self.seo_page.slug)
    
    def test_public_get_unpublished_page_returns_404(self):
        """Test that unpublished pages are not accessible via public API."""
        self.seo_page.is_published = False
        self.seo_page.save()
        
        response = self.client.get(f'/api/v1/public/seo-pages/{self.seo_page.slug}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_public_list_seo_pages(self):
        """Test public endpoint to list published SEO pages."""
        response = self.client.get('/api/v1/public/seo-pages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return published pages
        results = response.data.get('results', [])
        for page in results:
            self.assertTrue(page.get('is_published', False))


class GuestOrderAPITestCase(TestCase):
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
    
    def test_start_guest_order_requires_website_id(self):
        """Test that website_id is required."""
        response = self.client.post('/api/v1/orders/guest-orders/start/', {
            'email': 'guest@example.com',
            'order_data': {}
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_start_guest_order_requires_email(self):
        """Test that email is required."""
        response = self.client.post('/api/v1/orders/guest-orders/start/', {
            'website_id': self.website.id,
            'order_data': {}
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_start_guest_order_checks_guest_checkout_enabled(self):
        """Test that guest checkout must be enabled."""
        self.website.allow_guest_checkout = False
        self.website.save()
        
        response = self.client.post('/api/v1/orders/guest-orders/start/', {
            'website_id': self.website.id,
            'email': 'guest@example.com',
            'order_data': {
                'topic': 'Test',
                'paper_type_id': 1,
                'number_of_pages': 5,
                'client_deadline': '2025-12-10T12:00:00Z',
                'order_instructions': 'Test instructions'
            }
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_verify_email_requires_token(self):
        """Test that verification token is required."""
        response = self.client.post('/api/v1/orders/guest-orders/verify-email/', {
            'website_id': self.website.id,
            'order_data': {}
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

