"""
Payment Reminder Models - Deadline percentage-based reminders
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from websites.models import Website


class PaymentReminderConfig(models.Model):
    """
    Configuration for payment reminders based on deadline percentage.
    Admin can create multiple reminders that trigger at different percentages
    of the deadline (e.g., 30%, 50%, 80%).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='payment_reminder_configs',
        help_text="Website this reminder config applies to"
    )
    name = models.CharField(
        max_length=255,
        help_text="Name/description for this reminder (e.g., 'First Reminder', 'Final Warning')"
    )
    deadline_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of deadline elapsed when to send (e.g., 30.00 for 30%)"
    )
    message = models.TextField(
        help_text="Message to send in notification/email"
    )
    send_as_notification = models.BooleanField(
        default=True,
        help_text="Send as in-app notification"
    )
    send_as_email = models.BooleanField(
        default=True,
        help_text="Send as email"
    )
    email_subject = models.CharField(
        max_length=255,
        blank=True,
        help_text="Email subject (if blank, uses default)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this reminder is active"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for displaying reminders (lower = earlier)"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_payment_reminders',
        help_text="Admin who created this reminder"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'deadline_percentage']
        unique_together = ['website', 'deadline_percentage']
        verbose_name = "Payment Reminder Configuration"
        verbose_name_plural = "Payment Reminder Configurations"

    def __str__(self):
        return f"{self.name} ({self.deadline_percentage}%) - {self.website.name}"


class PaymentReminderDeletionMessage(models.Model):
    """
    Message to send after payment deadline has elapsed (order deleted/cancelled).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='payment_deletion_messages',
        help_text="Website this message applies to"
    )
    message = models.TextField(
        help_text="Message to send when order is deleted after deadline"
    )
    send_as_notification = models.BooleanField(
        default=True,
        help_text="Send as in-app notification"
    )
    send_as_email = models.BooleanField(
        default=True,
        help_text="Send as email"
    )
    email_subject = models.CharField(
        max_length=255,
        blank=True,
        help_text="Email subject (if blank, uses default)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this deletion message is active"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_deletion_messages',
        help_text="Admin who created this message"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Deletion Message"
        verbose_name_plural = "Payment Deletion Messages"

    def __str__(self):
        return f"Deletion Message - {self.website.name}"


class PaymentReminderSent(models.Model):
    """
    Tracks which reminders have been sent to which orders/payments
    to prevent duplicate sends.
    """
    reminder_config = models.ForeignKey(
        PaymentReminderConfig,
        on_delete=models.CASCADE,
        related_name='sent_reminders'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment_reminders_sent',
        null=True,
        blank=True
    )
    payment = models.ForeignKey(
        'order_payments_management.OrderPayment',
        on_delete=models.CASCADE,
        related_name='reminders_sent',
        null=True,
        blank=True
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_as_notification = models.BooleanField(default=False)
    sent_as_email = models.BooleanField(default=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_reminders_received'
    )

    class Meta:
        unique_together = ['reminder_config', 'order', 'payment']
        indexes = [
            models.Index(fields=['order', 'reminder_config']),
            models.Index(fields=['payment', 'reminder_config']),
            models.Index(fields=['client', 'sent_at']),
        ]

    def __str__(self):
        target = f"Order {self.order.id}" if self.order else f"Payment {self.payment.id}"
        return f"{self.reminder_config.name} sent to {target} at {self.sent_at}"

