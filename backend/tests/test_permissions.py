"""
Tests for permission and authorization.
"""
import pytest
from rest_framework import status
from tests.factories import (
    ClientUserFactory, WriterUserFactory, AdminUserFactory,
    OrderFactory, WebsiteFactory
)


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.auth
class TestRoleBasedAccess:
    """Tests for role-based access control."""
    
    def test_client_cannot_access_admin_endpoints(
        self, authenticated_client
    ):
        """Test that clients cannot access admin-only endpoints."""
        url = '/api/v1/admin-management/users/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_access_admin_endpoints(
        self, authenticated_admin_client
    ):
        """Test that admins can access admin endpoints."""
        url = '/api/v1/admin-management/users/'
        response = authenticated_admin_client.get(url)
        
        # Should not be 403, might be 200 or 404 depending on implementation
        assert response.status_code != status.HTTP_403_FORBIDDEN
    
    def test_writer_cannot_access_client_orders(
        self, authenticated_writer_client, website
    ):
        """Test that writers cannot access other users' orders directly."""
        other_client = ClientUserFactory(website=website)
        order = OrderFactory(client=other_client, website=website)
        
        url = f'/api/v1/orders/orders/{order.id}/'
        response = authenticated_writer_client.get(url)
        
        # Should be forbidden or not found
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]
    
    def test_client_can_access_own_orders(
        self, authenticated_client, client_user
    ):
        """Test that clients can access their own orders."""
        order = OrderFactory(client=client_user)
        
        url = f'/api/v1/orders/orders/{order.id}/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.auth
class TestAuthenticationRequired:
    """Tests that endpoints require authentication."""
    
    def test_orders_list_requires_auth(self, api_client):
        """Test orders list requires authentication."""
        url = '/api/v1/orders/orders/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_user_profile_requires_auth(self, api_client):
        """Test user profile requires authentication."""
        url = '/api/v1/users/profile/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_endpoints_require_auth(self, api_client):
        """Test admin endpoints require authentication."""
        url = '/api/v1/admin-management/users/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

