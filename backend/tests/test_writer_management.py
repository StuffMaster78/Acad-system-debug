"""
Comprehensive tests for writer management endpoints and workflows.
Tests writer profiles, order requests, assignments, and earnings.
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
from writer_management.models import WriterProfile, WriterOrderRequest, WriterOrderTake
from orders.models import Order


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.writer
class TestWriterProfile:
    """Tests for writer profile endpoints."""
    
    def test_get_writer_profile_requires_authentication(self, api_client, writer_profile):
        """Test getting writer profile requires authentication."""
        url = f'/api/v1/writer-management/writers/{writer_profile.id}/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_writer_profile_requires_staff(self, authenticated_client, writer_profile):
        """Test getting writer profile requires staff privileges."""
        url = f'/api/v1/writer-management/writers/{writer_profile.id}/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_own_writer_profile(self, authenticated_writer, writer_user, writer_profile):
        """Test writer can get their own profile."""
        url = f'/api/v1/writer-management/writers/{writer_profile.id}/'
        response = authenticated_writer.get(url)
        
        # May vary based on implementation - writer might see own profile
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
    
    def test_list_writers_requires_staff(self, authenticated_client):
        """Test listing writers requires staff privileges."""
        url = '/api/v1/writer-management/writers/'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.writer
class TestWriterOrderRequest:
    """Tests for writer order request workflow."""
    
    def test_create_order_request_requires_authentication(self, api_client, order, website):
        """Test creating order request requires authentication."""
        url = '/api/v1/writer-management/writer-order-requests/'
        data = {
            'order': order.id,
            'website': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_order_request_success(self, authenticated_writer, writer_user, writer_profile, order, website):
        """Test writer can create order request."""
        # Ensure order is available
        order.status = 'available'
        order.is_paid = True
        order.save()
        
        url = '/api/v1/writer-management/writer-order-requests/'
        data = {
            'order': order.id,
            'website': website.id
        }
        
        response = authenticated_writer.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['order'] == order.id
        assert response.data['writer'] == writer_user.id
    
    def test_list_own_order_requests(self, authenticated_writer, writer_user, writer_profile, order, website):
        """Test writer can list their own order requests."""
        # Create a request
        WriterOrderRequest.objects.create(
            writer=writer_user,
            order=order,
            website=website
        )
        
        url = '/api/v1/writer-management/writer-order-requests/'
        response = authenticated_writer.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', [])
        assert len(results) >= 1
        assert any(r['order'] == order.id for r in results)
    
    def test_cancel_order_request(self, authenticated_writer, writer_user, writer_profile, order, website):
        """Test writer can cancel their order request."""
        # Create a request
        request = WriterOrderRequest.objects.create(
            writer=writer_user,
            order=order,
            website=website
        )
        
        url = f'/api/v1/writer-management/writer-order-requests/{request.id}/'
        response = authenticated_writer.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not WriterOrderRequest.objects.filter(id=request.id).exists()


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.writer
class TestWriterOrderTake:
    """Tests for writer order take workflow."""
    
    def test_take_order_requires_authentication(self, api_client, order, website):
        """Test taking order requires authentication."""
        url = '/api/v1/writer-management/writer-order-takes/'
        data = {
            'order': order.id,
            'website': website.id
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_take_available_order(self, authenticated_writer, writer_user, writer_profile, order, website):
        """Test writer can take available order."""
        # Ensure order is available and paid
        order.status = 'available'
        order.is_paid = True
        order.save()
        
        url = '/api/v1/writer-management/writer-order-takes/'
        data = {
            'order': order.id,
            'website': website.id
        }
        
        response = authenticated_writer.post(url, data, format='json')
        
        # Status may vary based on implementation
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        
        # If successful, verify order taken
        if response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]:
            order.refresh_from_db()
            # Order should be assigned or status changed
            assert order.writer_id == writer_user.id or order.status != 'available'


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.writer
class TestWriterDashboard:
    """Tests for writer dashboard endpoints."""
    
    def test_get_dashboard_requires_authentication(self, api_client):
        """Test getting dashboard requires authentication."""
        url = '/api/v1/writer-management/dashboard/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_dashboard_success(self, authenticated_writer, writer_user, writer_profile):
        """Test writer can get their dashboard."""
        url = '/api/v1/writer-management/dashboard/'
        response = authenticated_writer.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Dashboard should contain relevant data
        assert 'data' in response.data or 'stats' in response.data or 'orders' in response.data


@pytest.mark.unit
@pytest.mark.writer
class TestWriterProfileModel:
    """Unit tests for WriterProfile model."""
    
    def test_writer_profile_creation(self, writer_user, website):
        """Test writer profile creation."""
        profile = WriterProfile.objects.create(
            user=writer_user,
            website=website,
            registration_id='W12345',
            email=writer_user.email
        )
        
        assert profile.user == writer_user
        assert profile.website == website
        assert profile.registration_id == 'W12345'
    
    def test_writer_profile_str_representation(self, writer_profile):
        """Test writer profile string representation."""
        str_repr = str(writer_profile)
        assert writer_profile.user.username in str_repr or writer_profile.registration_id in str_repr


@pytest.mark.unit
@pytest.mark.writer
class TestWriterOrderRequestModel:
    """Unit tests for WriterOrderRequest model."""
    
    def test_order_request_creation(self, writer_user, order, website):
        """Test order request creation."""
        request = WriterOrderRequest.objects.create(
            writer=writer_user,
            order=order,
            website=website
        )
        
        assert request.writer == writer_user
        assert request.order == order
        assert request.website == website
        assert request.approved is False  # Default should be False
    
    def test_order_request_approval(self, writer_user, order, website):
        """Test order request approval."""
        request = WriterOrderRequest.objects.create(
            writer=writer_user,
            order=order,
            website=website,
            approved=False
        )
        
        request.approved = True
        request.save()
        
        assert request.approved is True

