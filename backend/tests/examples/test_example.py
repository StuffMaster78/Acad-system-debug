"""
Example test file demonstrating testing patterns and best practices.

This file serves as a reference for writing tests in the Writing System Platform.
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tests.factories import (
    ClientUserFactory, WriterUserFactory, OrderFactory,
    WebsiteFactory, ClientWalletFactory
)

User = get_user_model()


# ============================================================================
# Example: Unit Test (Fast, Isolated)
# ============================================================================

@pytest.mark.unit
class TestUserModel:
    """Example unit tests for User model."""
    
    def test_user_creation(self, website):
        """Test that a user can be created."""
        user = ClientUserFactory(website=website)
        assert user.id is not None
        assert user.email is not None
        assert user.role == 'client'
        assert user.is_active is True
    
    def test_user_str_representation(self, client_user):
        """Test user string representation."""
        assert str(client_user) == client_user.email or str(client_user.username)


# ============================================================================
# Example: API Test (Integration with Database)
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
class TestAuthenticationAPI:
    """Example API tests for authentication endpoints."""
    
    def test_user_registration(self, api_client, website):
        """Test user registration endpoint."""
        url = '/api/v1/auth/auth/register/'
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'TestPass123!',
            'role': 'client',
            'website': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == data['email']
    
    def test_user_login(self, api_client, client_user):
        """Test user login endpoint."""
        url = '/api/v1/auth/auth/login/'
        data = {
            'email': client_user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_with_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        url = '/api/v1/auth/auth/login/'
        data = {
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Example: Authenticated API Test
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
@pytest.mark.client
class TestOrderAPI:
    """Example API tests for order endpoints."""
    
    def test_create_order(self, authenticated_client, client_user, website):
        """Test creating an order as authenticated client."""
        url = '/api/v1/orders/orders/'
        data = {
            'title': 'Test Order',
            'description': 'This is a test order',
            'pages': 5,
            'academic_level': 'undergraduate',
            'paper_type': 'essay',
            'deadline': '2025-12-31T23:59:59Z',
            'website': website.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
        assert response.data['client'] == client_user.id
    
    def test_list_orders(self, authenticated_client, client_user):
        """Test listing orders for authenticated client."""
        # Create some test orders
        OrderFactory.create_batch(3, client=client_user)
        
        url = '/api/v1/orders/orders/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_get_order_detail(self, authenticated_client, client_user):
        """Test retrieving order details."""
        order = OrderFactory(client=client_user)
        
        url = f'/api/v1/orders/orders/{order.id}/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id
        assert response.data['title'] == order.title
    
    def test_unauthorized_access(self, api_client):
        """Test that unauthenticated users cannot access orders."""
        url = '/api/v1/orders/orders/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# Example: Role-Based Access Control Test
# ============================================================================

@pytest.mark.api
@pytest.mark.integration
@pytest.mark.auth
class TestRoleBasedAccess:
    """Example tests for role-based access control."""
    
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


# ============================================================================
# Example: Using Fixtures and Factories
# ============================================================================

@pytest.mark.integration
class TestWithFactories:
    """Example tests using factories for test data."""
    
    def test_order_with_factory(self, website):
        """Test using OrderFactory to create test data."""
        client = ClientUserFactory(website=website)
        order = OrderFactory(client=client, website=website)
        
        assert order.client == client
        assert order.website == website
        assert order.title is not None
        assert order.price is not None
    
    def test_batch_creation(self, website):
        """Test creating multiple objects with factories."""
        clients = ClientUserFactory.create_batch(5, website=website)
        assert len(clients) == 5
        
        for client in clients:
            assert client.website == website
            assert client.role == 'client'


# ============================================================================
# Example: Performance Test
# ============================================================================

@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Example performance tests."""
    
    def test_bulk_order_creation(self, authenticated_client, client_user, website):
        """Test creating many orders efficiently."""
        url = '/api/v1/orders/orders/'
        
        orders_data = [
            {
                'title': f'Order {i}',
                'description': f'Description for order {i}',
                'pages': 5,
                'academic_level': 'undergraduate',
                'paper_type': 'essay',
                'deadline': '2025-12-31T23:59:59Z',
                'website': website.id
            }
            for i in range(10)
        ]
        
        import time
        start_time = time.time()
        
        for data in orders_data:
            response = authenticated_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
        
        elapsed_time = time.time() - start_time
        
        # Should create 10 orders in less than 5 seconds
        assert elapsed_time < 5.0, f"Bulk creation took {elapsed_time:.2f}s, expected < 5s"

