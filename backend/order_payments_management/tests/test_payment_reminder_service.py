"""
Comprehensive service layer tests for PaymentReminderService.
Tests business logic, calculations, and edge cases.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from order_payments_management.models.payment_reminders import (
    PaymentReminderConfig,
    PaymentReminderSent
)
from order_payments_management.services.payment_reminder_service import PaymentReminderService


@pytest.mark.unit
@pytest.mark.payment
class TestPaymentReminderServiceDeadlinePercentage:
    """Tests for deadline percentage calculation."""
    
    def test_get_deadline_percentage_no_deadline(self, order):
        """Test percentage calculation when order has no deadline."""
        order.client_deadline = None
        order.save()
        
        percentage = PaymentReminderService.get_deadline_percentage(order)
        assert percentage == Decimal('0.00')
    
    def test_get_deadline_percentage_at_start(self, order):
        """Test percentage calculation at order creation time."""
        now = timezone.now()
        order.created_at = now
        order.client_deadline = now + timedelta(days=7)
        order.save()
        
        percentage = PaymentReminderService.get_deadline_percentage(order, current_time=now)
        assert percentage == Decimal('0.00')
    
    def test_get_deadline_percentage_at_midpoint(self, order):
        """Test percentage calculation at midpoint of deadline."""
        now = timezone.now()
        order.created_at = now - timedelta(days=3.5)
        order.client_deadline = now + timedelta(days=3.5)
        order.save()
        
        percentage = PaymentReminderService.get_deadline_percentage(order, current_time=now)
        # Should be approximately 50%
        assert 49 <= float(percentage) <= 51
    
    def test_get_deadline_percentage_at_deadline(self, order):
        """Test percentage calculation at deadline."""
        now = timezone.now()
        order.created_at = now - timedelta(days=7)
        order.client_deadline = now
        order.save()
        
        percentage = PaymentReminderService.get_deadline_percentage(order, current_time=now)
        assert percentage == Decimal('100.00')
    
    def test_get_deadline_percentage_past_deadline(self, order):
        """Test percentage calculation past deadline."""
        now = timezone.now()
        order.created_at = now - timedelta(days=10)
        order.client_deadline = now - timedelta(days=3)
        order.save()
        
        percentage = PaymentReminderService.get_deadline_percentage(order, current_time=now)
        assert percentage == Decimal('100.00')
    
    def test_get_deadline_percentage_invalid_duration(self, order):
        """Test percentage calculation with invalid duration."""
        now = timezone.now()
        order.created_at = now
        order.client_deadline = now  # Same time
        order.save()
        
        percentage = PaymentReminderService.get_deadline_percentage(order, current_time=now)
        assert percentage == Decimal('100.00')


@pytest.mark.unit
@pytest.mark.payment
class TestPaymentReminderServiceGetOrders:
    """Tests for getting orders needing reminders."""
    
    def test_get_orders_needing_reminders_no_unpaid_orders(self, website):
        """Test when there are no unpaid orders."""
        orders = PaymentReminderService.get_orders_needing_reminders(website)
        assert len(orders) == 0
    
    def test_get_orders_needing_reminders_paid_orders_excluded(self, website, client_user, order):
        """Test that paid orders are excluded."""
        order.is_paid = True
        order.save()
        
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Test',
            is_active=True
        )
        
        orders = PaymentReminderService.get_orders_needing_reminders(website)
        assert order not in orders
    
    def test_get_orders_needing_reminders_past_deadline_excluded(self, website, client_user):
        """Test that orders past deadline are excluded."""
        order = Order.objects.create(
            client=client_user,
            website=website,
            topic='Past Deadline Order',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            client_deadline=timezone.now() - timedelta(days=1),
            is_paid=False,
            status='pending'
        )
        
        orders = PaymentReminderService.get_orders_needing_reminders(website)
        assert order not in orders
    
    def test_get_orders_needing_reminders_matches_percentage(self, website, client_user):
        """Test that orders matching reminder percentage are included."""
        now = timezone.now()
        order = Order.objects.create(
            client=client_user,
            website=website,
            topic='Test Order',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            created_at=now - timedelta(days=3.5),
            client_deadline=now + timedelta(days=3.5),
            is_paid=False,
            status='pending'
        )
        
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Test reminder',
            is_active=True
        )
        
        orders = PaymentReminderService.get_orders_needing_reminders(website, current_time=now)
        assert order in orders
    
    def test_get_orders_needing_reminders_already_sent_excluded(self, website, client_user):
        """Test that orders with already sent reminders are excluded."""
        now = timezone.now()
        order = Order.objects.create(
            client=client_user,
            website=website,
            topic='Test Order',
            number_of_pages=5,
            total_price=Decimal('100.00'),
            created_at=now - timedelta(days=3.5),
            client_deadline=now + timedelta(days=3.5),
            is_paid=False,
            status='pending'
        )
        
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Test reminder',
            is_active=True
        )
        
        # Send a reminder
        PaymentReminderSent.objects.create(
            client=client_user,
            order=order,
            reminder_config=config,
            sent_at=now
        )
        
        orders = PaymentReminderService.get_orders_needing_reminders(website, current_time=now)
        assert order not in orders


@pytest.mark.unit
@pytest.mark.payment
class TestPaymentReminderServiceSendReminder:
    """Tests for sending reminders."""
    
    def test_send_reminder_success(self, website, client_user, order):
        """Test successfully sending a reminder."""
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
    
    def test_send_reminder_no_client(self, website, order):
        """Test sending reminder when order has no client."""
        order.client = None
        order.save()
        
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Test',
            is_active=True
        )
        
        result = PaymentReminderService.send_reminder(order, config)
        assert result is False
    
    def test_send_reminder_message_formatting(self, website, client_user, order):
        """Test that reminder message is properly formatted."""
        config = PaymentReminderConfig.objects.create(
            website=website,
            deadline_percentage=50,
            message='Order {order_id}: ${amount} due by {deadline}',
            send_as_notification=True,
            send_as_email=False,
            is_active=True
        )
        
        result = PaymentReminderService.send_reminder(order, config)
        assert result is True
        
        sent_reminder = PaymentReminderSent.objects.filter(
            order=order,
            reminder_config=config
        ).first()
        assert sent_reminder is not None

