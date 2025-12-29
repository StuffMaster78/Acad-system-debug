"""
Comprehensive tests for OrderRevisionService.

Tests cover:
- Revision deadline calculation
- Revision period validation
- Revision request permissions
- Requesting revisions
- Processing revisions
- Edge cases
"""
import pytest
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from orders.models import Order, OrderTransitionLog
from orders.order_enums import OrderStatus
from orders.services.revisions import OrderRevisionService
from order_configs.models import OrderConfig


@pytest.mark.django_db
class TestOrderRevisionService:
    """Test OrderRevisionService functionality."""
    
    def test_get_revision_deadline_with_config(self, order, website):
        """Test getting revision deadline from config."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        service = OrderRevisionService(order, order.client)
        deadline = service.get_revision_deadline()
        
        assert deadline == timedelta(days=14)
    
    def test_get_revision_deadline_no_config(self, order):
        """Test getting revision deadline raises error when no config."""
        # Delete any existing configs
        OrderConfig.objects.filter(website=order.website).delete()
        
        service = OrderRevisionService(order, order.client)
        
        with pytest.raises(Exception):  # PolicyNotFound
            service.get_revision_deadline()
    
    def test_is_within_revision_period_not_completed(self, order):
        """Test revision period check for non-completed orders."""
        order.status = OrderStatus.SUBMITTED.value
        order.save()
        
        service = OrderRevisionService(order, order.client)
        assert service.is_within_revision_period() is True
    
    def test_is_within_revision_period_completed_within_deadline(self, order, website):
        """Test revision period check for completed order within deadline."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        # Create transition log showing completion 5 days ago
        OrderTransitionLog.objects.create(
            order=order,
            old_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.COMPLETED.value,
            timestamp=timezone.now() - timedelta(days=5)
        )
        
        service = OrderRevisionService(order, order.client)
        assert service.is_within_revision_period() is True
    
    def test_is_within_revision_period_completed_outside_deadline(self, order, website):
        """Test revision period check for completed order outside deadline."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=7,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        # Create transition log showing completion 10 days ago
        OrderTransitionLog.objects.create(
            order=order,
            old_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.COMPLETED.value,
            timestamp=timezone.now() - timedelta(days=10)
        )
        
        service = OrderRevisionService(order, order.client)
        assert service.is_within_revision_period() is False
    
    def test_can_request_revision_completed_as_client(self, order, website, client_user):
        """Test client can request revision for completed order."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.client = client_user
        order.save()
        
        OrderTransitionLog.objects.create(
            order=order,
            old_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.COMPLETED.value,
            timestamp=timezone.now() - timedelta(days=5)
        )
        
        service = OrderRevisionService(order, client_user)
        assert service.can_request_revision() is True
    
    def test_can_request_revision_completed_wrong_client(self, order, website, client_user, writer_user):
        """Test wrong client cannot request revision."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.client = client_user
        order.save()
        
        service = OrderRevisionService(order, writer_user)
        
        with pytest.raises(PermissionDenied):
            service.can_request_revision()
    
    def test_can_request_revision_completed_as_admin(self, order, website, admin_user):
        """Test admin can request revision for any completed order."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.save()
        
        service = OrderRevisionService(order, admin_user)
        assert service.can_request_revision() is True
    
    def test_can_request_revision_non_completed(self, order, client_user):
        """Test can request revision for non-completed orders."""
        order.status = OrderStatus.SUBMITTED.value
        order.client = client_user
        order.save()
        
        service = OrderRevisionService(order, client_user)
        assert service.can_request_revision() is True
    
    def test_request_revision_success(self, order, website, client_user):
        """Test successfully requesting revision."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.client = client_user
        order.save()
        
        OrderTransitionLog.objects.create(
            order=order,
            old_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.COMPLETED.value,
            timestamp=timezone.now() - timedelta(days=5)
        )
        
        service = OrderRevisionService(order, client_user)
        result = service.request_revision("Need more details")
        
        assert result is True
        order.refresh_from_db()
        assert order.revision_request == "Need more details"
        assert order.status == OrderStatus.REVISION_REQUESTED.value
    
    def test_request_revision_fails_when_not_allowed(self, order, website, client_user):
        """Test revision request fails when not allowed."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=7,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.client = client_user
        order.save()
        
        # Completed 10 days ago (outside deadline)
        OrderTransitionLog.objects.create(
            order=order,
            old_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.COMPLETED.value,
            timestamp=timezone.now() - timedelta(days=10)
        )
        
        service = OrderRevisionService(order, client_user)
        result = service.request_revision("Too late")
        
        assert result is False
    
    def test_process_revision_success(self, order, writer_user):
        """Test successfully processing revision."""
        order.status = OrderStatus.REVISION_IN_PROGRESS.value
        order.assigned_writer = writer_user
        order.save()
        
        service = OrderRevisionService(order, writer_user)
        result = service.process_revision("Revised work content")
        
        assert result is True
        order.refresh_from_db()
        assert order.revised_work == "Revised work content"
        assert order.status == OrderStatus.REVISED.value
    
    def test_process_revision_wrong_status(self, order, writer_user):
        """Test processing revision fails from wrong status."""
        order.status = OrderStatus.IN_PROGRESS.value
        order.save()
        
        service = OrderRevisionService(order, writer_user)
        result = service.process_revision("Revised work")
        
        assert result is False
        order.refresh_from_db()
        assert order.status == OrderStatus.IN_PROGRESS.value  # Unchanged


@pytest.mark.django_db
class TestOrderRevisionServiceEdgeCases:
    """Test edge cases for revision service."""
    
    def test_revision_deadline_fallback_to_updated_at(self, order, website):
        """Test revision period uses updated_at when no transition log."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=7,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.updated_at = timezone.now() - timedelta(days=5)
        order.save()
        
        service = OrderRevisionService(order, order.client)
        assert service.is_within_revision_period() is True
    
    def test_revision_request_updates_revision_request_field(self, order, website, client_user):
        """Test revision request updates the revision_request field."""
        OrderConfig.objects.create(
            website=website,
            free_revision_days=14,
            is_active=True
        )
        
        order.status = OrderStatus.COMPLETED.value
        order.client = client_user
        order.save()
        
        OrderTransitionLog.objects.create(
            order=order,
            old_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.COMPLETED.value,
            timestamp=timezone.now() - timedelta(days=5)
        )
        
        service = OrderRevisionService(order, client_user)
        service.request_revision("Test revision reason")
        
        order.refresh_from_db()
        assert order.revision_request == "Test revision reason"

