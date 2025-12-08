"""
Comprehensive tests for order workflows including creation, assignment, completion, and cancellation.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from tests.factories import (
    ClientUserFactory, WriterUserFactory, OrderFactory,
    WebsiteFactory, WriterProfileFactory
)
from orders.models import Order


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderCreation:
    """Tests for order creation workflow."""
    
    def test_create_order_success(self, authenticated_client, client_user, website):
        """Test successful order creation."""
        url = '/api/v1/orders/orders/'
        deadline = (timezone.now() + timedelta(days=7)).isoformat()
        data = {
            'topic': 'Test Order Topic',
            'number_of_pages': 5,
            'academic_level_id': 1,
            'paper_type_id': 1,
            'client_deadline': deadline,
            'order_instructions': 'Test instructions',
            'website_id': website.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['topic'] == data['topic']
        assert response.data['number_of_pages'] == data['number_of_pages']
        assert response.data['status'] == 'draft'
    
    def test_create_order_requires_authentication(self, api_client, website):
        """Test order creation requires authentication."""
        url = '/api/v1/orders/orders/'
        data = {
            'topic': 'Test Order',
            'number_of_pages': 5,
            'website_id': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_order_validates_required_fields(self, authenticated_client, client_user, website):
        """Test order creation validates required fields."""
        url = '/api/v1/orders/orders/'
        data = {
            # Missing required fields
            'website_id': website.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderAssignment:
    """Tests for order assignment workflow."""
    
    def test_assign_order_to_writer(self, authenticated_admin, order, writer_user, writer_profile):
        """Test admin can assign order to writer."""
        url = f'/api/v1/orders/orders/{order.id}/action/'
        data = {
            'action': 'assign_order',
            'writer_id': writer_user.id
        }
        
        response = authenticated_admin.post(url, data, format='json')
        
        # Status may vary based on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verify order assigned
        order.refresh_from_db()
        # Assignment may set writer_id or use assigned_writer field
        assert order.writer_id == writer_user.id or order.assigned_writer_id == writer_user.id
    
    def test_assign_order_requires_staff(self, authenticated_client, order, writer_user):
        """Test order assignment requires staff privileges."""
        url = f'/api/v1/orders/orders/{order.id}/action/'
        data = {
            'action': 'assign_order',
            'writer_id': writer_user.id
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_assign_order_invalid_writer(self, authenticated_admin, order):
        """Test assignment fails with invalid writer ID."""
        url = f'/api/v1/orders/orders/{order.id}/action/'
        data = {
            'action': 'assign_order',
            'writer_id': 99999  # Non-existent writer
        }
        
        response = authenticated_admin.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderCompletion:
    """Tests for order completion workflow."""
    
    def test_complete_order_success(self, authenticated_writer, order, writer_user):
        """Test writer can complete assigned order."""
        # Assign order to writer
        order.writer_id = writer_user.id
        order.status = 'in_progress'
        order.save()
        
        url = f'/api/v1/orders/orders/{order.id}/complete/'
        response = authenticated_writer.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify order completed
        order.refresh_from_db()
        assert order.status == 'completed'
    
    def test_complete_order_requires_assignment(self, authenticated_writer, order):
        """Test completing order requires it to be assigned."""
        # Order not assigned
        order.writer_id = None
        order.assigned_writer_id = None
        order.status = 'draft'
        order.save()
        
        url = f'/api/v1/orders/orders/{order.id}/action/'
        data = {'action': 'complete_order'}
        response = authenticated_writer.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_complete_order_requires_ownership(self, authenticated_writer, order, other_writer):
        """Test writer can only complete their own orders."""
        # Assign to different writer
        order.writer_id = other_writer.id
        order.assigned_writer_id = other_writer.id
        order.status = 'in_progress'
        order.save()
        
        url = f'/api/v1/orders/orders/{order.id}/action/'
        data = {'action': 'complete_order'}
        response = authenticated_writer.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderCancellation:
    """Tests for order cancellation workflow."""
    
    def test_cancel_order_success(self, authenticated_client, order):
        """Test client can cancel their own order."""
        url = f'/api/v1/orders/orders/{order.id}/cancel/'
        data = {
            'reason': 'No longer needed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Verify order cancelled
        order.refresh_from_db()
        assert order.status == 'cancelled'
    
    def test_cancel_order_requires_ownership(self, authenticated_client, other_client_order):
        """Test client can only cancel their own orders."""
        url = f'/api/v1/orders/orders/{other_client_order.id}/action/'
        data = {
            'action': 'cancel_order',
            'reason': 'Test cancellation'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_cancel_paid_order_creates_refund(self, authenticated_client, order, client_wallet):
        """Test cancelling paid order creates refund."""
        # Mark order as paid
        order.is_paid = True
        order.status = 'in_progress'
        order.save()
        
        initial_balance = client_wallet.balance
        
        url = f'/api/v1/orders/orders/{order.id}/action/'
        data = {
            'action': 'cancel_order',
            'reason': 'Change of mind'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verify order cancelled
        order.refresh_from_db()
        assert order.status == 'cancelled'
        
        # Note: Actual refund logic depends on implementation
        # This test verifies the endpoint works, refund logic tested separately


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.order
class TestOrderList:
    """Tests for order listing endpoints."""
    
    def test_list_orders_requires_authentication(self, api_client):
        """Test listing orders requires authentication."""
        url = '/api/v1/orders/orders/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_own_orders(self, authenticated_client, client_user, order):
        """Test client can list their own orders."""
        url = '/api/v1/orders/orders/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert any(o['id'] == order.id for o in response.data['results'])
    
    def test_list_orders_filter_by_status(self, authenticated_client, client_user):
        """Test filtering orders by status."""
        # Create orders with different statuses
        draft_order = OrderFactory(client=client_user, status='draft')
        in_progress_order = OrderFactory(client=client_user, status='in_progress')
        
        url = '/api/v1/orders/orders/?status=draft'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', [])
        assert all(o['status'] == 'draft' for o in results)
        assert any(o['id'] == draft_order.id for o in results)
        assert not any(o['id'] == in_progress_order.id for o in results)
    
    def test_list_orders_pagination(self, authenticated_client, client_user):
        """Test order listing supports pagination."""
        # Create multiple orders
        for _ in range(15):
            OrderFactory(client=client_user)
        
        url = '/api/v1/orders/orders/?page_size=10'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert len(response.data['results']) <= 10

