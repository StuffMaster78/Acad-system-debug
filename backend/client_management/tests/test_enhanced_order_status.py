"""
Tests for enhanced order status endpoint.
Tests the /api/v1/client-management/dashboard/enhanced-order-status/ endpoint.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from writer_management.models import WriterProfile


@pytest.mark.api
@pytest.mark.integration
class TestEnhancedOrderStatus:
    """Tests for enhanced order status endpoint."""
    
    def test_enhanced_order_status_requires_auth(self, api_client):
        """Test enhanced order status requires authentication."""
        url = '/api/v1/client-management/dashboard/enhanced-order-status/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_enhanced_order_status_client_only(self, authenticated_writer_client):
        """Test only clients can access enhanced order status."""
        url = '/api/v1/client-management/dashboard/enhanced-order-status/'
        response = authenticated_writer_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_enhanced_order_status_success(self, authenticated_client, client_user, website, order):
        """Test successful enhanced order status retrieval."""
        url = '/api/v1/client-management/dashboard/enhanced-order-status/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'orders' in response.data
        assert isinstance(response.data['orders'], list)
    
    def test_enhanced_order_status_includes_all_fields(self, authenticated_client, client_user, website, order):
        """Test enhanced order status includes all required fields."""
        # Assign a writer to the order
        from conftest import writer_user
        writer_profile = WriterProfile.objects.create(
            user=writer_user,
            website=website,
            is_available_for_auto_assignments=True
        )
        order.assigned_writer = writer_user
        order.status = 'in_progress'
        order.save()
        
        url = '/api/v1/client-management/dashboard/enhanced-order-status/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        orders = response.data['orders']
        if orders:
            order_data = orders[0]
            assert 'id' in order_data
            assert 'status' in order_data
            assert 'total_price' in order_data
            assert 'client_deadline' in order_data
            assert 'assigned_writer' in order_data or 'writer' in order_data
    
    def test_enhanced_order_status_filters_by_client(self, authenticated_client, client_user, website, other_client):
        """Test enhanced order status only shows client's own orders."""
        # Create order for authenticated client
        my_order = Order.objects.create(
            client=client_user,
            website=website,
            topic='My Order',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            client_deadline=timezone.now() + timedelta(days=7),
            status='pending'
        )
        
        # Create order for another client
        other_order = Order.objects.create(
            client=other_client,
            website=website,
            topic='Other Order',
            number_of_pages=3,
            total_price=Decimal('50.00'),
            client_deadline=timezone.now() + timedelta(days=5),
            status='pending'
        )
        
        url = '/api/v1/client-management/dashboard/enhanced-order-status/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        orders = response.data['orders']
        order_ids = [o['id'] for o in orders]
        assert my_order.id in order_ids
        assert other_order.id not in order_ids
    
    def test_enhanced_order_status_includes_progress(self, authenticated_client, client_user, website, order):
        """Test enhanced order status includes progress information."""
        order.status = 'in_progress'
        order.save()
        
        url = '/api/v1/client-management/dashboard/enhanced-order-status/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        orders = response.data['orders']
        if orders:
            order_data = orders[0]
            # Progress should be included for in-progress orders
            if order_data['status'] == 'in_progress':
                assert 'progress' in order_data or 'progress_percentage' in order_data

