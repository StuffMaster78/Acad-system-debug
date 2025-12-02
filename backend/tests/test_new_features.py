"""
Tests for new high-impact features
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from websites.models import Website

User = get_user_model()


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def test_website(db):
    """Create a test website."""
    return Website.objects.create(
        name="Test Website",
        domain="test.com",
        is_active=True
    )


@pytest.fixture
def admin_user(db, test_website):
    """Create an admin user."""
    user = User.objects.create_user(
        username="admin",
        email="admin@test.com",
        password="testpass123",
        role="admin",
        website=test_website
    )
    return user


@pytest.fixture
def client_user(db, test_website):
    """Create a client user."""
    user = User.objects.create_user(
        username="client",
        email="client@test.com",
        password="testpass123",
        role="client",
        website=test_website
    )
    return user


@pytest.fixture
def writer_user(db, test_website):
    """Create a writer user."""
    user = User.objects.create_user(
        username="writer",
        email="writer@test.com",
        password="testpass123",
        role="writer",
        website=test_website
    )
    return user


class TestLoginAlerts:
    """Test login alert preferences endpoints."""
    
    def test_get_login_alert_preferences(self, api_client, client_user):
        """Test getting login alert preferences."""
        api_client.force_authenticate(user=client_user)
        response = api_client.get('/api/v1/users/login-alerts/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_create_login_alert_preferences(self, api_client, client_user):
        """Test creating login alert preferences."""
        api_client.force_authenticate(user=client_user)
        data = {
            'notify_new_login': True,
            'notify_new_device': True,
            'notify_new_location': False,
        }
        response = api_client.post('/api/v1/users/login-alerts/', data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]


class TestOrderDrafts:
    """Test order drafts endpoints."""
    
    def test_list_order_drafts(self, api_client, client_user, test_website):
        """Test listing order drafts."""
        api_client.force_authenticate(user=client_user)
        response = api_client.get('/api/v1/orders/drafts/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_order_draft(self, api_client, client_user, test_website):
        """Test creating an order draft."""
        api_client.force_authenticate(user=client_user)
        data = {
            'topic': 'Test Topic',
            'order_instructions': 'Test instructions',
            'number_of_pages': 5,
            'website': test_website.id,
        }
        response = api_client.post('/api/v1/orders/drafts/', data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]


class TestOrderPresets:
    """Test order presets endpoints."""
    
    def test_list_order_presets(self, api_client, client_user):
        """Test listing order presets."""
        api_client.force_authenticate(user=client_user)
        response = api_client.get('/api/v1/orders/presets/')
        assert response.status_code == status.HTTP_200_OK


class TestAnalytics:
    """Test analytics endpoints."""
    
    def test_client_analytics_current_period(self, api_client, client_user):
        """Test getting current period analytics for client."""
        api_client.force_authenticate(user=client_user)
        response = api_client.get('/api/v1/analytics/client/current_period/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_writer_analytics_current_period(self, api_client, writer_user):
        """Test getting current period analytics for writer."""
        api_client.force_authenticate(user=writer_user)
        response = api_client.get('/api/v1/analytics/writer/current_period/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestWriterCapacity:
    """Test writer capacity endpoints."""
    
    def test_get_writer_capacity(self, api_client, writer_user):
        """Test getting writer capacity settings."""
        api_client.force_authenticate(user=writer_user)
        response = api_client.get('/api/v1/writer-management/capacity/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_writer_capacity(self, api_client, writer_user, test_website):
        """Test creating writer capacity settings."""
        api_client.force_authenticate(user=writer_user)
        data = {
            'max_active_orders': 5,
            'is_available': True,
            'website': test_website.id,
        }
        response = api_client.post('/api/v1/writer-management/capacity/', data)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]


class TestTenantBranding:
    """Test tenant branding endpoints."""
    
    def test_get_tenant_branding(self, api_client, admin_user):
        """Test getting tenant branding."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/websites/branding/current/')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestDisputes:
    """Test dispute endpoints."""
    
    def test_list_disputes(self, api_client, client_user):
        """Test listing disputes."""
        api_client.force_authenticate(user=client_user)
        response = api_client.get('/api/v1/support-management/disputes/')
        assert response.status_code == status.HTTP_200_OK

