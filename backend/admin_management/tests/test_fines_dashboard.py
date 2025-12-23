"""
Tests for admin fines dashboard endpoints.
Tests analytics, dispute queue, and active fines endpoints.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from fines.models import Fine, FineAppeal
from orders.models import Order
from writer_management.models import WriterProfile


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.admin
class TestFinesAnalytics:
    """Tests for fines analytics endpoint."""
    
    def test_fines_analytics_requires_auth(self, api_client):
        """Test fines analytics requires authentication."""
        url = '/api/v1/admin-management/fines/analytics/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_fines_analytics_admin_only(self, authenticated_client):
        """Test only admins can access fines analytics."""
        url = '/api/v1/admin-management/fines/analytics/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_fines_analytics_success(self, authenticated_admin_client, admin_user, website, writer_user, order):
        """Test successful fines analytics retrieval."""
        # Create a fine
        from fines.models import FineStatus
        fine = Fine.objects.create(
            order=order,
            writer=writer_user,
            website=website,
            fine_type='late_submission',
            amount=Decimal('50.00'),
            status=FineStatus.ISSUED,
            reason='Late submission'
        )
        
        url = '/api/v1/admin-management/fines/analytics/'
        response = authenticated_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data or 'total_fines' in response.data
    
    def test_fines_analytics_includes_statistics(self, authenticated_admin_client, website, writer_user):
        """Test fines analytics includes statistics."""
        # Create multiple fines with different statuses
        Fine.objects.create(
            writer=writer_user,
            website=website,
            fine_type='late_submission',
            amount=Decimal('50.00'),
            status='active',
            reason='Late submission'
        )
        Fine.objects.create(
            writer=writer_user,
            website=website,
            fine_type='quality_issue',
            amount=Decimal('75.00'),
            status='paid',
            reason='Quality issue'
        )
        
        url = '/api/v1/admin-management/fines/analytics/'
        response = authenticated_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.data
        # Should include counts or totals
        assert 'total_fines' in data or 'active_fines' in data or 'total_amount' in data


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.admin
class TestFinesDisputeQueue:
    """Tests for fines dispute queue endpoint."""
    
    def test_dispute_queue_requires_auth(self, api_client):
        """Test dispute queue requires authentication."""
        url = '/api/v1/admin-management/fines/dispute-queue/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_dispute_queue_admin_only(self, authenticated_client):
        """Test only admins can access dispute queue."""
        url = '/api/v1/admin-management/fines/dispute-queue/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_dispute_queue_success(self, authenticated_admin_client, website, writer_user):
        """Test successful dispute queue retrieval."""
        # Create a fine with an appeal
        fine = Fine.objects.create(
            writer=writer_user,
            website=website,
            fine_type='late_submission',
            amount=Decimal('50.00'),
            status='pending',
            reason='Late submission'
        )
        
        appeal = FineAppeal.objects.create(
            fine=fine,
            writer=writer_user,
            reason='I submitted on time',
            status='pending'
        )
        
        url = '/api/v1/admin-management/fines/dispute-queue/'
        response = authenticated_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    def test_approve_dispute(self, authenticated_admin_client, website, writer_user, order):
        """Test approving a dispute."""
        from fines.models import FineStatus
        fine = Fine.objects.create(
            order=order,
            writer=writer_user,
            website=website,
            fine_type='late_submission',
            amount=Decimal('50.00'),
            status=FineStatus.ISSUED,
            reason='Late submission'
        )
        
        appeal = FineAppeal.objects.create(
            fine=fine,
            writer=writer_user,
            reason='I submitted on time',
            status='pending'
        )
        
        url = f'/api/v1/admin-management/fines/{fine.id}/appeals/approve/'
        response = authenticated_admin_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        appeal.refresh_from_db()
        assert appeal.status == 'approved'
        fine.refresh_from_db()
        assert fine.status == FineStatus.WAIVED
    
    def test_reject_dispute(self, authenticated_admin_client, website, writer_user, order):
        """Test rejecting a dispute."""
        from fines.models import FineStatus
        fine = Fine.objects.create(
            order=order,
            writer=writer_user,
            website=website,
            fine_type='late_submission',
            amount=Decimal('50.00'),
            status=FineStatus.ISSUED,
            reason='Late submission'
        )
        
        appeal = FineAppeal.objects.create(
            fine=fine,
            writer=writer_user,
            reason='I submitted on time',
            status='pending'
        )
        
        url = f'/api/v1/admin-management/fines/{fine.id}/appeals/reject/'
        response = authenticated_admin_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        appeal.refresh_from_db()
        assert appeal.status == 'rejected'
        fine.refresh_from_db()
        assert fine.status == FineStatus.ISSUED


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.admin
class TestActiveFines:
    """Tests for active fines endpoint."""
    
    def test_active_fines_requires_auth(self, api_client):
        """Test active fines requires authentication."""
        url = '/api/v1/admin-management/fines/active/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_active_fines_admin_only(self, authenticated_client):
        """Test only admins can access active fines."""
        url = '/api/v1/admin-management/fines/active/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_active_fines_success(self, authenticated_admin_client, website, writer_user, order):
        """Test successful active fines retrieval."""
        from fines.models import FineStatus
        # Create active fines
        Fine.objects.create(
            order=order,
            writer=writer_user,
            website=website,
            fine_type='late_submission',
            amount=Decimal('50.00'),
            status=FineStatus.ISSUED,
            reason='Late submission'
        )
        Fine.objects.create(
            order=order,
            writer=writer_user,
            website=website,
            fine_type='quality_issue',
            amount=Decimal('75.00'),
            status=FineStatus.ISSUED,
            reason='Quality issue'
        )
        
        url = '/api/v1/admin-management/fines/pending/'
        response = authenticated_admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
        
        # Should only return pending/issued fines
        fines = response.data.get('results', response.data)
        for fine in fines:
            assert fine['status'] in ['issued', 'pending', FineStatus.ISSUED]

