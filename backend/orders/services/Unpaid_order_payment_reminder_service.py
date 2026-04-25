"""
Service for managing deadline percentage-based payment reminders.
"""
from decimal import Decimal
from typing import Dict, List, Optional, Any
import logging

from django.utils import timezone
from django.db.models import QuerySet

from orders.models.orders.order import Order
from order_payments_management.models.payment_reminders import (
    PaymentReminderConfig,
    PaymentReminderDeletionMessage,
    PaymentReminderSent,
)
from order_payments_management.models.payments import OrderPayment
from notifications_system.services.notification_service import (
    NotificationService,
)

logger = logging.getLogger(__name__)


class PaymentReminderService:
    """
    Service for calculating and sending payment reminders based on
    deadline percentages.
    """

    @staticmethod
    def get_deadline_percentage(
        order: Order,
        current_time=None,
    ) -> Decimal:
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
            return Decimal("0.00")

        order_created = order.created_at
        deadline = order.client_deadline

        total_duration = deadline - order_created
        elapsed = current_time - order_created

        if total_duration.total_seconds() <= 0:
            return Decimal("100.00")

        percentage = (
            elapsed.total_seconds() / total_duration.total_seconds()
        ) * 100

        return Decimal(str(min(max(percentage, 0), 100)))

    @staticmethod
    def get_orders_needing_reminders(
        website,
        current_time=None,
    ) -> List[dict[str, Any]]:
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

        unpaid_orders = Order.objects.filter(
            website=website,
            client_deadline__isnull=False,
            client_deadline__gt=current_time,
        ).select_related("client", "website")

        reminder_configs = PaymentReminderConfig.objects.filter(
            website=website,
            is_active=True,
        ).order_by("deadline_percentage")

        orders_needing_reminders = []

        for order in unpaid_orders:
            unpaid_payments = OrderPayment.objects.filter(
                order=order,
                status__in=["pending", "unpaid"],
            ).exists()

            if not unpaid_payments and order.status not in [
                "pending",
                "unpaid",
            ]:
                continue

            current_percentage = (
                PaymentReminderService.get_deadline_percentage(
                    order,
                    current_time,
                )
            )

            for config in reminder_configs:
                if current_percentage >= config.deadline_percentage:
                    already_sent = PaymentReminderSent.objects.filter(
                        reminder_config=config,
                        order=order,
                    ).exists()

                    if not already_sent:
                        orders_needing_reminders.append(
                            {
                                "order": order,
                                "config": config,
                                "percentage": current_percentage,
                            }
                        )
                        break

        return orders_needing_reminders

    @staticmethod
    def send_reminder(
        order: Order,
        config: PaymentReminderConfig,
    ) -> bool:
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
                logger.warning(
                    "Order %s has no client, skipping reminder",
                    order.pk,
                )
                return False

            message = config.message.format(
                order_id=order.pk,
                topic=order.topic,
                amount=order.total_price,
                deadline=(
                    order.client_deadline.strftime("%Y-%m-%d %H:%M")
                    if order.client_deadline else "N/A"
                ),
            )

            if config.send_as_notification:
                try:
                    NotificationService.notify(
                        event_key="payment.reminder",
                        recipient=client,
                        website=order.website,
                        context={
                            "order_id": order.pk,
                            "topic": order.topic,
                            "amount": order.total_price,
                            "deadline": (
                                order.client_deadline.strftime(
                                    "%Y-%m-%d %H:%M"
                                )
                                if order.client_deadline else "N/A"
                            ),
                            "message": message,
                            "link": f"/orders/{order.pk}/pay",
                        },
                        channels=["email", "in_app"],
                        triggered_by=None,
                        priority="normal",
                        is_broadcast=False,
                        is_critical=False,
                        is_digest=False,
                        is_silent=False,
                        digest_group=None,
                    )
                except Exception as exc:
                    logger.error(
                        "Failed to send notification reminder: %s",
                        exc,
                    )

            if config.send_as_email:
                try:
                    from django.conf import settings
                    from django.core.mail import send_mail

                    subject = (
                        config.email_subject
                        or "Payment Reminder - Action Required"
                    )
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False,
                    )
                except Exception as exc:
                    logger.error(
                        "Failed to send email reminder: %s",
                        exc,
                    )

            payment = OrderPayment.objects.filter(
                order=order,
                status__in=["pending", "unpaid"],
            ).first()

            PaymentReminderSent.objects.create(
                reminder_config=config,
                order=order,
                payment=payment,
                client=client,
                sent_as_notification=config.send_as_notification,
                sent_as_email=config.send_as_email,
            )

            logger.info(
                "Payment reminder '%s' sent for order %s",
                config.name,
                order.pk,
            )
            return True

        except Exception as exc:
            logger.error("Error sending payment reminder: %s", exc)
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

            deletion_message = (
                PaymentReminderDeletionMessage.objects.filter(
                    website=website,
                    is_active=True,
                ).first()
            )

            if not deletion_message:
                logger.warning(
                    "No deletion message configured for website %s",
                    website.id,
                )
                return False

            message = deletion_message.message.format(
                order_id=order.pk,
                topic=order.topic,
                deadline=(
                    order.client_deadline.strftime("%Y-%m-%d %H:%M")
                    if order.client_deadline else "N/A"
                ),
            )

            if deletion_message.send_as_notification:
                try:
                    NotificationService.notify(
                        event_key="payment.deleted",
                        recipient=client,
                        website=website,
                        context={
                            "order_id": order.pk,
                            "topic": order.topic,
                            "deadline": (
                                order.client_deadline.strftime(
                                    "%Y-%m-%d %H:%M"
                                )
                                if order.client_deadline else "N/A"
                            ),
                            "message": message,
                        },
                        channels=["email", "in_app"],
                        triggered_by=None,
                        priority="high",
                        is_broadcast=False,
                        is_critical=True,
                        is_digest=False,
                        is_silent=False,
                        digest_group=None,
                    )
                except Exception as exc:
                    logger.error(
                        "Failed to send deletion notification: %s",
                        exc,
                    )

            if deletion_message.send_as_email:
                try:
                    from django.conf import settings
                    from django.core.mail import send_mail

                    subject = (
                        deletion_message.email_subject
                        or "Order Deleted - Payment Deadline Passed"
                    )
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[client.email],
                        fail_silently=False,
                    )
                except Exception as exc:
                    logger.error(
                        "Failed to send deletion email: %s",
                        exc,
                    )

            logger.info("Deletion message sent for order %s", order.pk)
            return True

        except Exception as exc:
            logger.error("Error sending deletion message: %s", exc)
            return False

    @staticmethod
    def get_orders_past_deadline(
        website,
        current_time=None,
    ) -> QuerySet[Order]:
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
            status__in=["pending", "unpaid"],
        ).select_related("client", "website")