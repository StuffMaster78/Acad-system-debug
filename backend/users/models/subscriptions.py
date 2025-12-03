"""
Client Subscription Management Models
Manages various subscription types for clients including newsletters, blog posts, coupons, etc.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from websites.models import Website
from django.utils import timezone


class SubscriptionType(models.TextChoices):
    """Types of subscriptions available to clients."""
    NEWSLETTER = 'newsletter', _('Newsletter')
    BLOG_POSTS = 'blog_posts', _('Blog Post Updates')
    COUPON_UPDATES = 'coupon_updates', _('Coupon Updates')
    MARKETING_MESSAGES = 'marketing_messages', _('Marketing Messages')
    UNREAD_MESSAGES = 'unread_messages', _('Unread Messages')
    TRANSACTIONAL_MESSAGES = 'transactional_messages', _('Transactional Messages')
    NOTIFICATIONS = 'notifications', _('Notifications')
    ORDER_UPDATES = 'order_updates', _('Order Updates')
    PROMOTIONAL_OFFERS = 'promotional_offers', _('Promotional Offers')
    PRODUCT_UPDATES = 'product_updates', _('Product Updates')
    SECURITY_ALERTS = 'security_alerts', _('Security Alerts')
    ACCOUNT_UPDATES = 'account_updates', _('Account Updates')


class DeliveryChannel(models.TextChoices):
    """Channels through which subscriptions can be delivered."""
    EMAIL = 'email', _('Email')
    SMS = 'sms', _('SMS')
    PUSH = 'push', _('Push Notification')
    IN_APP = 'in_app', _('In-App Notification')


class ClientSubscription(models.Model):
    """
    Manages client subscriptions to various types of communications.
    Clients can subscribe/unsubscribe to different types of messages.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        limit_choices_to={'role__in': ['client', 'customer']},
        help_text=_("The client user who has this subscription.")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='client_subscriptions',
        help_text=_("The website this subscription is associated with.")
    )
    subscription_type = models.CharField(
        max_length=50,
        choices=SubscriptionType.choices,
        help_text=_("Type of subscription.")
    )
    is_subscribed = models.BooleanField(
        default=True,
        help_text=_("Whether the client is currently subscribed.")
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the client first subscribed.")
    )
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the client unsubscribed, if applicable.")
    )
    last_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the last message of this type was sent.")
    )
    preferred_channels = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Preferred delivery channels for this subscription type.")
    )
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', _('Immediate')),
            ('daily', _('Daily Digest')),
            ('weekly', _('Weekly Digest')),
            ('monthly', _('Monthly Digest')),
        ],
        default='immediate',
        help_text=_("How frequently to receive messages.")
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata for the subscription.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Client Subscription")
        verbose_name_plural = _("Client Subscriptions")
        unique_together = ('user', 'website', 'subscription_type')
        indexes = [
            models.Index(fields=['user', 'website']),
            models.Index(fields=['subscription_type', 'is_subscribed']),
            models.Index(fields=['is_subscribed']),
        ]

    def __str__(self):
        status = "Subscribed" if self.is_subscribed else "Unsubscribed"
        return f"{self.user.email} - {self.get_subscription_type_display()} ({status})"

    def subscribe(self):
        """Subscribe the client to this subscription type."""
        self.is_subscribed = True
        self.unsubscribed_at = None
        self.save(update_fields=['is_subscribed', 'unsubscribed_at', 'updated_at'])

    def unsubscribe(self):
        """Unsubscribe the client from this subscription type."""
        self.is_subscribed = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_subscribed', 'unsubscribed_at', 'updated_at'])

    def update_last_sent(self):
        """Update the last sent timestamp."""
        self.last_sent_at = timezone.now()
        self.save(update_fields=['last_sent_at', 'updated_at'])


class SubscriptionPreference(models.Model):
    """
    Global subscription preferences for a client.
    Provides a centralized way to manage all subscription settings.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription_preferences',
        limit_choices_to={'role__in': ['client', 'customer']},
        help_text=_("The client user.")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='subscription_preferences',
        help_text=_("The website these preferences are for.")
    )
    # Global settings
    all_subscriptions_enabled = models.BooleanField(
        default=True,
        help_text=_("Master switch for all subscriptions.")
    )
    marketing_consent = models.BooleanField(
        default=False,
        help_text=_("Consent to receive marketing communications.")
    )
    marketing_consent_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When marketing consent was given.")
    )
    # Channel preferences
    email_enabled = models.BooleanField(
        default=True,
        help_text=_("Enable email delivery.")
    )
    sms_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable SMS delivery.")
    )
    push_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable push notifications.")
    )
    in_app_enabled = models.BooleanField(
        default=True,
        help_text=_("Enable in-app notifications.")
    )
    # Do not disturb settings
    dnd_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable do-not-disturb hours.")
    )
    dnd_start_hour = models.PositiveSmallIntegerField(
        default=22,
        help_text=_("Do-not-disturb start hour (0-23).")
    )
    dnd_end_hour = models.PositiveSmallIntegerField(
        default=6,
        help_text=_("Do-not-disturb end hour (0-23).")
    )
    # Transactional messages cannot be disabled
    transactional_enabled = models.BooleanField(
        default=True,
        help_text=_("Transactional messages (cannot be disabled).")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Subscription Preference")
        verbose_name_plural = _("Subscription Preferences")
        unique_together = ('user', 'website')

    def __str__(self):
        return f"Subscription Preferences for {self.user.email}"

    def is_in_dnd_hours(self):
        """Check if current time is within do-not-disturb hours."""
        if not self.dnd_enabled:
            return False
        now = timezone.now()
        current_hour = now.hour
        if self.dnd_start_hour > self.dnd_end_hour:
            # DND spans midnight
            return current_hour >= self.dnd_start_hour or current_hour < self.dnd_end_hour
        else:
            return self.dnd_start_hour <= current_hour < self.dnd_end_hour

