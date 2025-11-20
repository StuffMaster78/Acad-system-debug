from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from websites.models import Website
from writer_management.models.profile import WriterProfile
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake,
    WriterOrderHoldRequest, WriterReassignmentRequest
)

class WebhookPlatform(models.TextChoices):
    """Available platforms for webhooks."""
    SLACK = "slack", "Slack"
    DISCORD = "discord", "Discord"
    TELEGRAM = "telegram", "Telegram"


class WebhookSettings(models.Model):
    """
    Stores webhook settings for a writer.
    """
    from orders.order_enums import WebhookEvent

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="webhook_settings",
        help_text="The user this webhook setting belongs to."
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="webhook_settings",
        help_text="Multitenancy support: this webhook is for a specific website."
    )
    platform = models.CharField(
        max_length=20,
        choices=WebhookPlatform.choices,
        help_text="The platform for the webhook (e.g., Slack, Discord)."
    )
    webhook_url = models.URLField(
        help_text="The URL to which the webhook will send requests."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="If false, this webhook won't send any events."
    )
    subscribed_events = ArrayField(
        models.CharField(
            max_length=50,
            choices=WebhookEvent.choices
        ),
        default=list,
        blank=True,
        help_text="List of events this webhook is subscribed to."
    )
    is_active = models.BooleanField(
        default=True,
        help_text= (
            "Soft delete flag — deactivates the webhook "
            "without removing the record."
        )
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "platform", "website")
        verbose_name = "Webhook Setting"
        verbose_name_plural = "Webhook Settings"

    def __str__(self):
        return f"{self.user} – {self.platform} webhook"
    

class WriterOrderRequestNotification(models.Model):
    """
    Notifications for writers about their order requests.
    """
    request = models.ForeignKey(
        WriterOrderRequest, on_delete=models.CASCADE,
        related_name="notifications"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_request_notifications"
    )
    notification_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the notification was sent."
    )
    message = models.TextField(
        help_text="Notification message content."
    )

    def __str__(self):
        return f"Notification: {self.writer.user.username} - Request {self.request.id}"
    
    class Meta:
        verbose_name = "Writer Order Request Notification"
        verbose_name_plural = "Writer Order Request Notifications"
        ordering = ['-notification_date']


class WriterOrderTakeNotification(models.Model):
    """
    Notifications for writers about their order takes.
    """
    take = models.ForeignKey(
        WriterOrderTake, on_delete=models.CASCADE,
        related_name="notifications"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_take_notifications"
    )
    notification_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the notification was sent."
    )
    message = models.TextField(
        help_text="Notification message content."
    )

    def __str__(self):
        return f"Notification: {self.writer.user.username} - Take {self.take.id}"
    
    class Meta:
        verbose_name = "Writer Order Take Notification"
        verbose_name_plural = "Writer Order Take Notifications"
        ordering = ['-notification_date']

class WriterOrderRequestNotification(models.Model):
    """
    Notifications for writers about their order requests.
    """
    request = models.ForeignKey(
        WriterOrderRequest, on_delete=models.CASCADE,
        related_name="notifications"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_request_notifications"
    )
    notification_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the notification was sent."
    )
    message = models.TextField(
        help_text="Notification message content."
    )

    def __str__(self):
        return f"Notification: {self.writer.user.username} - Request {self.request.id}"
    
    class Meta:
        verbose_name = "Writer Order Request Notification"
        verbose_name_plural = "Writer Order Request Notifications"
        ordering = ['-notification_date']


class WriterOrderTakeNotification(models.Model):
    """
    Notifications for writers about their order takes.
    """
    take = models.ForeignKey(
        WriterOrderTake, on_delete=models.CASCADE,
        related_name="notifications"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_take_notifications"
    )
    notification_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the notification was sent."
    )
    message = models.TextField(
        help_text="Notification message content."
    )

    def __str__(self):
        return f"Notification: {self.writer.user.username} - Take {self.take.id}"
    
    class Meta:
        verbose_name = "Writer Order Take Notification"
        verbose_name_plural = "Writer Order Take Notifications"
        ordering = ['-notification_date']


class WriterOrderHoldNotification(models.Model):
    """
    Notifications for writers about their order hold requests.
    """
    hold_request = models.ForeignKey(
        WriterOrderHoldRequest, on_delete=models.CASCADE,
        related_name="notifications"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="order_hold_notifications"
    )
    notification_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the notification was sent."
    )
    message = models.TextField(
        help_text="Notification message content."
    )

    def __str__(self):
        return f"Notification: {self.writer.user.username} - Hold Request {self.hold_request.id}"
    
    class Meta:
        verbose_name = "Writer Order Hold Notification"
        verbose_name_plural = "Writer Order Hold Notifications"
        ordering = ['-notification_date']


class WriterReassignmentNotification(models.Model):
    """
    Notifications for writers about their reassignment requests.
    """
    reassignment_request = models.ForeignKey(
        WriterReassignmentRequest, on_delete=models.CASCADE,
        related_name="notifications"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="reassignment_notifications"
    )
    notification_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the notification was sent."
    )
    message = models.TextField(
        help_text="Notification message content."
    )

    def __str__(self):
        return f"Notification: {self.writer.user.username} - Reassignment Request {self.reassignment_request.id}"
    
    class Meta:
        verbose_name = "Writer Reassignment Notification"
        verbose_name_plural = "Writer Reassignment Notifications"
        ordering = ['-notification_date']
