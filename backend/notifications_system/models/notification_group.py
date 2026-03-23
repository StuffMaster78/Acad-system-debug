from django.db import models
from django.conf import settings
from notifications_system.enums import NotificationChannel, NotificationPriority


class NotificationGroup(models.Model):
    """
    A named group of users sharing notification settings.
    Scoped per website — groups on different websites are independent.

    Examples: 'Daily Summaries', 'Order Alerts', 'VIP Client Updates'
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='notification_groups',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Supported channels for this group
    channels = models.JSONField(
        default=list,
        help_text="Delivery channels for this group e.g. ['email', 'in_app']",
    )
    default_channel = models.CharField(
        max_length=30,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
    )
    default_priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    is_active = models.BooleanField(default=True)
    is_enabled_by_default = models.BooleanField(
        default=True,
        help_text="Whether members receive notifications from this group by default.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notification_groups',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Group'
        verbose_name_plural = 'Notification Groups'
        # Name unique per website, not globally
        unique_together = ('website', 'name')
        ordering = ['name']
        indexes = [
            models.Index(fields=['website', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.website})"


class NotificationGroupMembership(models.Model):
    """
    Explicit membership of a user in a notification group.
    Separated from the group model to allow per-membership metadata
    such as when the user joined and who added them.
    """
    group = models.ForeignKey(
        NotificationGroup,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_group_memberships',
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_notification_group_memberships',
    )

    class Meta:
        verbose_name = 'Notification Group Membership'
        verbose_name_plural = 'Notification Group Memberships'
        unique_together = ('group', 'user')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user} in {self.group}"