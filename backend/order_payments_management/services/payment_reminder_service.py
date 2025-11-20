"""
Service for managing deadline percentage-based payment reminders.
"""
from decimal import Decimal
from typing import List, Optional, Dict
from django.utils import timezone
from django.db.models import Q
from orders.models import Order
from order_payments_management.models.payment_reminders import (
    PaymentReminderConfig,
    PaymentReminderSent,
    PaymentReminderDeletionMessage
)
from order_payments_management.models import OrderPayment
from notifications_system.services.core import NotificationService
from notifications_system.services.notification_helper import NotificationHelper
import logging

logger = logging.getLogger(__name__)


class PaymentReminderService:
    """
    Service for calculating and sending payment reminders based on deadline percentages.
    """

    @staticmethod
    def get_deadline_percentage(order: Order, current_time=None) -> Decimal:
        """
        Calculate what percentage of the deadline has elapsed.
        
        Args:
            order: The order to check
            current_time: Optional current time (for testing)
            
        Returns:
            Decimal percentage (0-100) of deadline elapsed
        """
        if current_time is None:
            current_time = timezone.now()
        
        if not order.client_deadline:
            return Decimal('0.00')
        
        # Calculate time elapsed since order creation
        order_created = order.created_at
        deadline = order.client_deadline
        
        total_duration = deadline - order_created
        elapsed = current_time - order_created
        
        if total_duration.total_seconds() <= 0:
            return Decimal('100.00')
        
        percentage = (elapsed.total_seconds() / total_duration.total_seconds()) * 100
        return Decimal(str(min(max(percentage, 0), 100)))

    @staticmethod
    def get_orders_needing_reminders(website, current_time=None) -> List[Order]:
        """
        Get orders that need reminders sent based on deadline percentage.
        
        Args:
            website: Website to filter by
            current_time: Optional current time (for testing)
            
        Returns:
            List of orders needing reminders
        """
        if current_time is None:
            current_time = timezone.now()
        
        # Get all unpaid orders with deadlines
        unpaid_orders = Order.objects.filter(
            website=website,
            client_deadline__isnull=False,
            client_deadline__gt=current_time  # Not yet past deadline
        ).select_related('client', 'website')
        
        # Get active reminder configs for this website
        reminder_configs = PaymentReminderConfig.objects.filter(
            website=website,
            is_active=True
        ).order_by('deadline_percentage')
        
        orders_needing_reminders = []
        
        for order in unpaid_orders:
            # Check if order has unpaid payments or if order itself is unpaid
            unpaid_payments = OrderPayment.objects.filter(
                order=order,
                status__in=['pending', 'unpaid']
            ).exists()
            
            # Also check if order status indicates it needs payment
            # Orders that are pending and haven't been paid yet
            if not unpaid_payments and order.status not in ['pending', 'unpaid']:
                continue
            
            # Calculate current deadline percentage
            current_percentage = PaymentReminderService.get_deadline_percentage(
                order, current_time
            )
            
            # Check each reminder config
            for config in reminder_configs:
                # Check if we should send this reminder
                if current_percentage >= config.deadline_percentage:
                    # Check if we've already sent this reminder
                    already_sent = PaymentReminderSent.objects.filter(
                        reminder_config=config,
                        order=order
                    ).exists()
                    
                    if not already_sent:
                        orders_needing_reminders.append({
                            'order': order,
                            'config': config,
                            'percentage': current_percentage
                        })
                        break  # Only send one reminder per check
        
        return orders_needing_reminders

    @staticmethod
    def send_reminder(order: Order, config: PaymentReminderConfig) -> bool:
        """
        Send a payment reminder for an order.
        
        Args:
            order: The order to send reminder for
            config: The reminder configuration to use
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            client = order.client
            if not client:
                logger.warning(f"Order {order.id} has no client, skipping reminder")
                return False
            
            # Format the message with order details
            message = config.message.format(
                order_id=order.id,
                topic=order.topic,
                amount=order.total_price,
                deadline=order.client_deadline.strftime('%Y-%m-%d %H:%M') if order.client_deadline else 'N/A'
            )
            
            # Send notification if enabled
            if config.send_as_notification:
                try:
                    NotificationHelper.send_notification(
                        user=client,
                        event_key='payment.reminder',
                        title='Payment Reminder',
                        message=message,
                        website=order.website,
                        link=f'/orders/{order.id}/pay'
                    )
                except Exception as e:
                    logger.error(f"Failed to send notification reminder: {e}")
            
            # Send email if enabled
            if config.send_as_email:
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    subject = config.email_subject or "Payment Reminder - Action Required"
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False
                    )
                except Exception as e:
                    logger.error(f"Failed to send email reminder: {e}")
            
            # Record that reminder was sent
            payment = OrderPayment.objects.filter(
                order=order,
                status__in=['pending', 'unpaid']
            ).first()
            
            PaymentReminderSent.objects.create(
                reminder_config=config,
                order=order,
                payment=payment,
                client=client,
                sent_as_notification=config.send_as_notification,
                sent_as_email=config.send_as_email
            )
            
            logger.info(f"Payment reminder '{config.name}' sent for order {order.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending payment reminder: {e}")
            return False

    @staticmethod
    def send_deletion_message(order: Order, website) -> bool:
        """
        Send deletion message after deadline has passed.
        
        Args:
            order: The order that was deleted
            website: Website context
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            client = order.client
            if not client:
                return False
            
            # Get active deletion message for website
            deletion_message = PaymentReminderDeletionMessage.objects.filter(
                website=website,
                is_active=True
            ).first()
            
            if not deletion_message:
                logger.warning(f"No deletion message configured for website {website.id}")
                return False
            
            # Format the message
            message = deletion_message.message.format(
                order_id=order.id,
                topic=order.topic,
                deadline=order.client_deadline.strftime('%Y-%m-%d %H:%M') if order.client_deadline else 'N/A'
            )
            
            # Send notification if enabled
            if deletion_message.send_as_notification:
                try:
                    NotificationHelper.send_notification(
                        user=client,
                        event_key='payment.deleted',
                        title='Order Deleted',
                        message=message,
                        website=website
                    )
                except Exception as e:
                    logger.error(f"Failed to send deletion notification: {e}")
            
            # Send email if enabled
            if deletion_message.send_as_email:
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    subject = deletion_message.email_subject or "Order Deleted - Payment Deadline Passed"
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False
                    )
                except Exception as e:
                    logger.error(f"Failed to send deletion email: {e}")
            
            logger.info(f"Deletion message sent for order {order.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending deletion message: {e}")
            return False

    @staticmethod
    def get_orders_past_deadline(website, current_time=None) -> List[Order]:
        """
        Get orders that are past their deadline and need deletion messages.
        
        Args:
            website: Website to filter by
            current_time: Optional current time (for testing)
            
        Returns:
            List of orders past deadline
        """
        if current_time is None:
            current_time = timezone.now()
        
        return Order.objects.filter(
            website=website,
            client_deadline__lt=current_time,
            status__in=['pending', 'unpaid']  # Only unpaid orders
        ).select_related('client', 'website')

