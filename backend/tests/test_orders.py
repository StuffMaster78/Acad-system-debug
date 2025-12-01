"""
Comprehensive tests for order endpoints.
"""
import pytest
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from tests.factories import (
    ClientUserFactory, WriterUserFactory, OrderFactory,
    WebsiteFactory, ClientWalletFactory
)


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderCreation:
    """Tests for order creation."""
    
    def test_create_order_requires_authentication(self, api_client):
        """Test creating order requires authentication."""
        url = '/api/v1/orders/orders/'
        data = {
            'title': 'Test Order',
            'pages': 5
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_order_success(self, authenticated_client, client_user, website):
        """Test successful order creation."""
        url = '/api/v1/orders/orders/'
        deadline = (timezone.now() + timedelta(days=7)).isoformat()
        data = {
            'title': 'Test Order',
            'description': 'This is a test order',
            'pages': 5,
            'academic_level': 'undergraduate',
            'paper_type': 'essay',
            'deadline': deadline,
            'website': website.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
        assert response.data['client'] == client_user.id
        assert response.data['pages'] == data['pages']
    
    def test_create_order_missing_required_fields(self, authenticated_client, website):
        """Test creating order without required fields fails."""
        url = '/api/v1/orders/orders/'
        data = {
            'title': 'Test Order'
            # Missing required fields
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_order_invalid_deadline(self, authenticated_client, website):
        """Test creating order with past deadline fails."""
        url = '/api/v1/orders/orders/'
        past_deadline = (timezone.now() - timedelta(days=1)).isoformat()
        data = {
            'title': 'Test Order',
            'pages': 5,
            'deadline': past_deadline,
            'website': website.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        # Should fail validation
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderRetrieval:
    """Tests for order retrieval."""
    
    def test_list_orders_requires_authentication(self, api_client):
        """Test listing orders requires authentication."""
        url = '/api/v1/orders/orders/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_own_orders(self, authenticated_client, client_user):
        """Test user can list their own orders."""
        # Create some orders for the client
        OrderFactory.create_batch(3, client=client_user)
        
        url = '/api/v1/orders/orders/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
        # Should see at least the orders we created
        orders = response.data.get('results', response.data)
        assert len(orders) >= 3
    
    def test_get_order_detail(self, authenticated_client, client_user):
        """Test user can get order details."""
        order = OrderFactory(client=client_user)
        
        url = f'/api/v1/orders/orders/{order.id}/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id
        assert response.data['title'] == order.title
    
    def test_cannot_access_other_user_order(self, authenticated_client, website):
        """Test user cannot access another user's order."""
        other_client = ClientUserFactory(website=website)
        order = OrderFactory(client=other_client)
        
        url = f'/api/v1/orders/orders/{order.id}/'
        response = authenticated_client.get(url)
        
        # Should be forbidden or not found
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderFiltering:
    """Tests for order filtering."""
    
    def test_filter_orders_by_status(self, authenticated_client, client_user):
        """Test filtering orders by status."""
        # Create orders with different statuses
        OrderFactory(client=client_user, status='pending')
        OrderFactory(client=client_user, status='assigned')
        OrderFactory(client=client_user, status='completed')
        
        url = '/api/v1/orders/orders/?status=pending'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        orders = response.data.get('results', response.data)
        # All returned orders should have pending status
        for order in orders:
            assert order['status'] == 'pending'
    
    def test_search_orders_by_title(self, authenticated_client, client_user):
        """Test searching orders by title."""
        OrderFactory(client=client_user, title='Important Order')
        OrderFactory(client=client_user, title='Another Order')
        
        url = '/api/v1/orders/orders/?search=Important'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        orders = response.data.get('results', response.data)
        # Should find the order with "Important" in title
        assert any('Important' in order.get('title', '') for order in orders)

