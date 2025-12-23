"""
Tests for payment reminder endpoints and services.
Tests POST/PATCH endpoints for creating and updating payment reminders.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from order_payments_management.models.payment_reminders import (
    PaymentReminderConfig,
    PaymentReminderSent,
    PaymentReminderDeletionMessage
)
from order_payments_management.services.payment_reminder_service import PaymentReminderService


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestPaymentReminderConfig:
    """Tests for payment reminder configuration endpoints."""
    
    def test_list_reminder_configs_requires_auth(self, api_client):
        """Test listing reminder configs requires authentication."""
        url = '/api/v1/order-payments/payment-reminder-configs/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_reminder_configs_admin_only(self, authenticated_client):
        """Test only admins can list reminder configs."""
        url = '/api/v1/order-payments/payment-reminder-configs/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_reminder_config(self, authenticated_admin_client, admin_user, website):
        """Test creating a payment reminder config."""
        url = '/api/v1/order-payments/payment-reminder-configs/'
        data = {
            'website': website.id,
            'deadline_percentage': 50,
            'message': 'Your order {order_id} payment is due. Amount: ${amount}',
            'send_as_notification': True,
            'send_as_email': True,
            'is_active': True,
            'display_order': 1
        }
        response = authenticated_admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['deadline_percentage'] == 50
        assert response.data['is_active'] is True
        assert response.data['created_by'] == admin_user.id
    
    def test_update_reminder_config(self, authenticated_admin_client, website):
        """Test updating a payment reminder config."""
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Original message',
            send_as_notification=True,
            send_as_email=True,
            is_active=True,
            display_order=1
        )
        url = f'/api/v1/order-payments/payment-reminder-configs/{config.id}/'
        data = {
            'message': 'Updated message',
            'deadline_percentage': 75
        }
        response = authenticated_admin_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        config.refresh_from_db()
        assert config.message == 'Updated message'
        assert config.deadline_percentage == 75
    
    def test_delete_reminder_config(self, authenticated_admin_client, website):
        """Test deleting a payment reminder config."""
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Test message',
            send_as_notification=True,
            send_as_email=True,
            is_active=True,
            display_order=1
        )
        url = f'/api/v1/order-payments/payment-reminder-configs/{config.id}/'
        response = authenticated_admin_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not PaymentReminderConfig.objects.filter(id=config.id).exists()


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestPaymentReminderService:
    """Tests for PaymentReminderService."""
    
    def test_get_orders_needing_reminders(self, website, client_user):
        """Test getting orders that need reminders."""
        # Create an unpaid order with deadline in the past
        order = Order.objects.create(
            client=client_user,
            website=website,
            topic='Test Order',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            client_deadline=timezone.now() - timedelta(days=1),
            is_paid=False,
            status='pending'
        )
        
        # Create reminder config for 50% deadline
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Payment reminder',
            send_as_notification=True,
            send_as_email=True,
            is_active=True
        )
        
        orders = PaymentReminderService.get_orders_needing_reminders(website)
        assert order in orders
    
    def test_send_reminder(self, website, client_user):
        """Test sending a payment reminder."""
        order = Order.objects.create(
            client=client_user,
            website=website,
            topic='Test Order',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            client_deadline=timezone.now() + timedelta(days=1),
            is_paid=False,
            status='pending'
        )
        
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Payment reminder for order {order_id}. Amount: ${amount}',
            send_as_notification=True,
            send_as_email=False,  # Disable email for testing
            is_active=True
        )
        
        result = PaymentReminderService.send_reminder(order, config)
        assert result is True
        
        # Verify reminder was sent
        sent_reminder = PaymentReminderSent.objects.filter(
            order=order,
            reminder_config=config
        ).first()
        assert sent_reminder is not None
        assert sent_reminder.client == client_user


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestPaymentReminderSent:
    """Tests for payment reminder sent tracking."""
    
    def test_list_sent_reminders_requires_auth(self, api_client):
        """Test listing sent reminders requires authentication."""
        url = '/api/v1/order-payments/payment-reminders-sent/'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_sent_reminders_for_client(self, authenticated_client, client_user, website, order):
        """Test client can list their own sent reminders."""
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Test reminder',
            send_as_notification=True,
            send_as_email=True,
            is_active=True
        )
        
        PaymentReminderSent.objects.create(
            client=client_user,
            order=order,
            reminder_config=config,
            sent_at=timezone.now()
        )
        
        url = '/api/v1/order-payments/payment-reminders-sent/'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.payment
class TestPaymentReminderDeletionMessage:
    """Tests for payment reminder deletion messages."""
    
    def test_create_deletion_message(self, authenticated_admin_client, website):
        """Test creating a deletion message for reminders."""
        url = '/api/v1/order-payments/payment-deletion-messages/'
        data = {
            'website': website.id,
            'message': 'This reminder has been deleted.',
            'is_active': True
        }
        response = authenticated_admin_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'This reminder has been deleted.'
    
    def test_update_deletion_message(self, authenticated_admin_client, website):
        """Test updating a deletion message."""
        message = PaymentReminderDeletionMessage.objects.create(
            website=website,
            message='Original message',
            is_active=True
        )
        url = f'/api/v1/order-payments/payment-deletion-messages/{message.id}/'
        data = {'message': 'Updated deletion message'}
        response = authenticated_admin_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        message.refresh_from_db()
        assert message.message == 'Updated deletion message'

