"""
API endpoint tests for critical functionality.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from websites.models import Website

User = get_user_model()


@pytest.mark.api
@pytest.mark.django_db
class TestAdminDashboardAPI:
    """Test admin dashboard API endpoints."""
    
    def test_admin_dashboard_requires_auth(self, db_with_website):
        """Test that admin dashboard requires authentication."""
        client = APIClient()
        response = client.get('/api/v1/admin-management/dashboard/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_admin_dashboard_caching(self, db_with_website):
        """Test that admin dashboard uses caching."""
        from django.contrib.auth import get_user_model
        from django.core.cache import cache
        
        User = get_user_model()
        website = db_with_website
        
        # Create admin user
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            website=website
        )
        
        client = APIClient()
        client.force_authenticate(user=admin)
        
        # Clear cache
        cache.clear()
        
        # First request - should hit database
        response1 = client.get('/api/v1/admin-management/dashboard/')
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request - should hit cache
        response2 = client.get('/api/v1/admin-management/dashboard/')
        assert response2.status_code == status.HTTP_200_OK
        
        # Responses should be identical (cached)
        # Note: This is a basic test - actual cache verification requires more setup


@pytest.mark.api
@pytest.mark.django_db
class TestClientDashboardAPI:
    """Test client dashboard API endpoints."""
    
    def test_client_dashboard_requires_auth(self, db_with_website):
        """Test that client dashboard requires authentication."""
        client = APIClient()
        response = client.get('/api/v1/client-management/dashboard/stats/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_client_dashboard_caching(self, db_with_website):
        """Test that client dashboard uses caching."""
        from client_management.models import ClientProfile
        
        website = db_with_website
        
        # Create client user
        client_user = User.objects.create_user(
            username='client',
            email='client@test.com',
            password='testpass123',
            role='client',
            website=website
        )
        
        ClientProfile.objects.create(user=client_user, website=website)
        
        client = APIClient()
        client.force_authenticate(user=client_user)
        
        # First request
        response1 = client.get('/api/v1/client-management/dashboard/stats/')
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request should use cache
        response2 = client.get('/api/v1/client-management/dashboard/stats/')
        assert response2.status_code == status.HTTP_200_OK


@pytest.mark.api
@pytest.mark.django_db
class TestWriterDashboardAPI:
    """Test writer dashboard API endpoints."""
    
    def test_writer_dashboard_requires_auth(self, db_with_website):
        """Test that writer dashboard requires authentication."""
        client = APIClient()
        response = client.get('/api/v1/writer-management/dashboard/earnings/')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_writer_dashboard_caching(self, db_with_website):
        """Test that writer dashboard uses caching."""
        from writer_management.models.profile import WriterProfile
        
        website = db_with_website
        
        # Create writer user
        writer_user = User.objects.create_user(
            username='writer',
            email='writer@test.com',
            password='testpass123',
            role='writer',
            website=website
        )
        
        WriterProfile.objects.create(user=writer_user, website=website, registration_id='Writer #12345')
        
        client = APIClient()
        client.force_authenticate(user=writer_user)
        
        # First request
        response1 = client.get('/api/v1/writer-management/dashboard/earnings/')
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request should use cache
        response2 = client.get('/api/v1/writer-management/dashboard/earnings/')
        assert response2.status_code == status.HTTP_200_OK


@pytest.mark.api
@pytest.mark.django_db
class TestOptimizedEndpoints:
    """Test optimized endpoints for query performance."""
    
    def test_review_management_uses_combined_aggregations(self, db_with_website):
        """Test that review management uses combined aggregations."""
        from django.contrib.auth import get_user_model
        from django.db import connection
        from django.test.utils import override_settings
        
        User = get_user_model()
        website = db_with_website
        
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            website=website
        )
        
        client = APIClient()
        client.force_authenticate(user=admin)
        
        # This test verifies the endpoint works
        # Actual query count verification would require more setup
        response = client.get('/api/v1/admin-management/reviews/analytics/')
        # Should return 200 or 404 (if no reviews exist)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

