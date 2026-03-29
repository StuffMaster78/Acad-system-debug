# notifications_system/admin.py
"""
Django admin registrations for the notification system.
Only registers models that exist in the current architecture.
"""
from __future__ import annotations

import json
import logging

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
    BroadcastOverride,
)
from notifications_system.models.delivery import Delivery
from notifications_system.models.digest_notifications import NotificationDigest
from notifications_system.models.event_config import NotificationEventConfig
from notifications_system.models.notification_event import (
    NotificationEvent as NotificationEventModel,
)
from notifications_system.models.notification_event_override import (
    NotificationEventOverride,
)
from notifications_system.models.notification_group import NotificationGroup
from notifications_system.models.notification_log import NotificationLog
from notifications_system.models.notification_preferences import (
    NotificationEventPreference,
    NotificationPreference,
    NotificationPreferenceProfile,
    RoleNotificationPreference,
)
from notifications_system.models.notification_settings import (
    GlobalNotificationSystemSettings,
)
from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_template import NotificationTemplate
from notifications_system.models.notifications_user_status import (
    NotificationsUserStatus,
)
from notifications_system.models.outbox import Outbox
from notifications_system.models.user_notification_meta import UserNotificationMeta

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Notification feed
# ─────────────────────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'event_key', 'category',
        'priority', 'status', 'is_broadcast', 'is_digest',
        'is_critical', 'sent_at', 'created_at', 'website',
    )
    search_fields = (
        'user__username', 'user__email',
        'event_key', 'category',
    )
    list_filter = (
        'category', 'priority', 'status',
        'is_broadcast', 'is_digest', 'is_critical',
        'website',
    )
    readonly_fields = (
        'user', 'website', 'event_key', 'category',
        'priority', 'status', 'channels',
        'is_broadcast', 'is_digest', 'is_critical',
        'is_silent', 'payload_pretty', 'rendered_pretty',
        'sent_at', 'expires_at',
        'created_at', 'updated_at',
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    actions = ['mark_sent', 'expire_notifications']

    def payload_pretty(self, obj):
        try:
            data = json.dumps(obj.payload, indent=2)
            return format_html(
                "<pre style='max-width:600px;overflow:auto'>{}</pre>",
                data,
            )
        except Exception:
            return str(obj.payload)
    payload_pretty.short_description = 'Payload'  # type: ignore[attr-defined]

    def rendered_pretty(self, obj):
        try:
            data = json.dumps(obj.rendered, indent=2)
            return format_html(
                "<pre style='max-width:600px;overflow:auto'>{}</pre>",
                data,
            )
        except Exception:
            return str(obj.rendered)
    rendered_pretty.short_description = 'Rendered'  # type: ignore[attr-defined]

    @admin.action(description='Mark selected as sent')
    def mark_sent(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='sent',
            sent_at=timezone.now(),
        )
        self.message_user(request, f"{updated} notification(s) marked as sent.")

    @admin.action(description='Expire selected notifications')
    def expire_notifications(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='cancelled',
            expires_at=timezone.now(),
        )
        self.message_user(request, f"{updated} notification(s) expired.")


@admin.register(NotificationsUserStatus)
class NotificationsUserStatusAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'notification', 'is_read',
        'is_pinned', 'is_acknowledged', 'priority', 'created_at',
    )
    list_filter = ('is_read', 'is_pinned', 'is_acknowledged', 'priority')
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'user', 'notification', 'website',
        'read_at', 'pinned_at', 'acknowledged_at', 'created_at',
    )


@admin.register(UserNotificationMeta)
class UserNotificationMetaAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'website', 'unread_count',
        'last_seen_at', 'last_notified_at', 'last_emailed_at',
    )
    search_fields = ('user__username', 'user__email')
    list_filter = ('website',)
    readonly_fields = (
        'user', 'website', 'unread_count',
        'last_seen_at', 'last_notified_at', 'last_emailed_at',
    )

    actions = ['reset_unread_count']

    @admin.action(description='Reset unread count to 0')
    def reset_unread_count(self, request, queryset):
        updated = queryset.update(unread_count=0)
        self.message_user(request, f"Reset unread count for {updated} user(s).")


# ─────────────────────────────────────────────────────────────
# Delivery pipeline
# ─────────────────────────────────────────────────────────────

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event_key', 'user', 'channel', 'status',
        'priority', 'attempts', 'max_retries',
        'queued_at', 'sent_at', 'triggered_by_fallback',
    )
    list_filter = ('status', 'channel', 'priority', 'triggered_by_fallback')
    search_fields = ('event_key', 'user__email', 'error_code')
    date_hierarchy = 'queued_at'
    readonly_fields = (
        'user', 'website', 'notification', 'event_key',
        'channel', 'priority', 'status',
        'attempts', 'max_retries',
        'provider_msg_id', 'error_code', 'error_detail',
        'queued_at', 'sent_at', 'next_retry_at',
        'triggered_by_fallback',
        'payload_pretty',
    )

    actions = ['retry_failed']

    def payload_pretty(self, obj):
        try:
            data = json.dumps(obj.payload, indent=2)
            return format_html(
                "<pre style='max-width:600px;overflow:auto'>{}</pre>",
                data,
            )
        except Exception:
            return str(obj.payload)
    payload_pretty.short_description = 'Payload'  # type: ignore[attr-defined]

    @admin.action(description='Retry failed deliveries')
    def retry_failed(self, request, queryset):
        from notifications_system.enums import DeliveryStatus
        from notifications_system.tasks.send import send_channel_notification

        retried = 0
        for delivery in queryset.filter(status=DeliveryStatus.FAILED):
            delivery.status = DeliveryStatus.QUEUED
            delivery.save(update_fields=['status'])
            send_channel_notification.delay(delivery.pk)  # type: ignore[attr-defined]
            retried += 1
        self.message_user(request, f"Retried {retried} delivery/deliveries.")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'event_key',
        'channel',
        'status',
        'is_successful',
        'attempt_number',
        'error_code',
        'attempted_at',
    )
    list_filter = ('status', 'channel', 'is_successful')
    search_fields = ('event_key', 'user__email', 'error_code')
    date_hierarchy = 'attempted_at'
    readonly_fields = (
        'user',
        'website',
        'notification',
        'delivery',
        'group',
        'event_key',
        'channel',
        'priority',
        'status',
        'response_code',
        'response_message',
        'error_code',
        'error_detail',
        'email_subject',
        'email_body',
        'payload',
        'attempt_number',
        'is_successful',
        'attempted_at',
    )


@admin.register(Outbox)
class OutboxAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event_key', 'user', 'status',
        'attempts', 'created_at', 'processed_at',
    )
    list_filter = ('status',)
    search_fields = ('event_key', 'user__email')
    date_hierarchy = 'created_at'
    readonly_fields = (
        'user', 'website', 'event_key', 'status',
        'dedupe_key', 'attempts', 'last_error',
        'created_at', 'processed_at',
    )

    actions = ['requeue_pending']

    @admin.action(description='Requeue selected pending outbox entries')
    def requeue_pending(self, request, queryset):
        from notifications_system.enums import DeliveryStatus
        from notifications_system.tasks.send import process_outbox_entry

        requeued = 0
        for outbox in queryset.filter(status='pending'):
            process_outbox_entry.delay(outbox.id)  # type: ignore[attr-defined]
            requeued += 1
        self.message_user(request, f"Requeued {requeued} outbox entry/entries.")


# ─────────────────────────────────────────────────────────────
# Events and config
# ─────────────────────────────────────────────────────────────

@admin.register(NotificationEventModel)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = (
        'event_key', 'label', 'category',
        'scope', 'is_active',
    )
    list_filter = ('category', 'scope', 'is_active')
    search_fields = ('event_key', 'label', 'description')
    ordering = ('category', 'event_key')

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(NotificationEventConfig)
class NotificationEventConfigAdmin(admin.ModelAdmin):
    list_display = (
        'event_key', 'priority', 'is_mandatory',
        'user_can_disable', 'digest_eligible',
        'cooldown_seconds', 'is_active', 'updated_at',
    )
    list_filter = (
        'priority', 'is_mandatory', 'user_can_disable',
        'digest_eligible', 'is_active',
        'supports_email', 'supports_in_app',
    )
    search_fields = ('event_key',)
    ordering = ('event_key',)
    readonly_fields = ('event_key', 'created_at', 'updated_at')


@admin.register(NotificationEventOverride)
class NotificationEventOverrideAdmin(admin.ModelAdmin):
    list_display = (
        'event_key', 'website', 'enabled',
        'priority', 'updated_at',
    )
    list_filter = ('website', 'enabled')
    search_fields = ('event_key',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': (
                'website', 'event_config',
                'enabled', 'priority',
                'channels', 'roles',
            ),
        }),
        ('Template & fallback', {
            'fields': ('template_key', 'fallback_message'),
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(
            "Admin updated NotificationEventOverride: %s website=%s",
            obj.event_key,
            getattr(obj.website, 'domain', None),
        )


# ─────────────────────────────────────────────────────────────
# Templates
# ─────────────────────────────────────────────────────────────

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'channel', 'website',
        'locale', 'version', 'is_active', 'updated_at',
    )
    list_filter = ('channel', 'website', 'locale', 'is_active')
    search_fields = ('event__event_key',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('event__event_key', 'channel', '-version')


# ─────────────────────────────────────────────────────────────
# Preferences
# ─────────────────────────────────────────────────────────────

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'website',
        'email_enabled', 'in_app_enabled',
        'dnd_enabled', 'mute_all',
        'digest_enabled', 'digest_frequency',
        'updated_at',
    )
    search_fields = ('user__username', 'user__email', 'website__domain')
    list_filter = (
        'website', 'email_enabled', 'in_app_enabled',
        'mute_all', 'dnd_enabled', 'digest_enabled',
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NotificationEventPreference)
class NotificationEventPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'event', 'website',
        'email_enabled', 'in_app_enabled',
        'is_enabled', 'updated_at',
    )
    list_filter = ('website', 'email_enabled', 'in_app_enabled', 'is_enabled')
    search_fields = ('user__username', 'user__email', 'event__event_key')
    readonly_fields = ('created_at', 'updated_at')

    actions = ['reset_to_defaults']

    @admin.action(description='Reset selected preferences to system defaults')
    def reset_to_defaults(self, request, queryset):
        from notifications_system.services.preference_service import (
            PreferenceService,
        )
        count = 0
        for pref in queryset.select_related('user', 'event'):
            PreferenceService._invalidate_cache(pref.user, pref.website)
            count += 1
        queryset.delete()
        self.message_user(
            request,
            f"Reset {count} event preference(s) to system defaults.",
        )


@admin.register(RoleNotificationPreference)
class RoleNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'role', 'website',
        'email_enabled', 'in_app_enabled',
        'digest_enabled', 'min_priority', 'updated_at',
    )
    list_filter = ('website', 'role')
    search_fields = ('role', 'website__domain')
    readonly_fields = ('updated_at',)


@admin.register(NotificationPreferenceProfile)
class NotificationPreferenceProfileAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'website',
        'email_enabled',
        'in_app_enabled',
        'dnd_enabled',
        'digest_enabled',
        'is_default',
        'updated_at',
    )
    search_fields = ('name', 'website__domain')
    list_filter = ('website', 'is_default')
    readonly_fields = ('created_at', 'updated_at')

    actions = ['apply_to_all_users_in_role']

    @admin.action(description='Apply profile to all users of its default role')
    def apply_to_all_users_in_role(self, request, queryset):
        from notifications_system.services.notification_profile_service import (
            NotificationProfileService,
        )
        from django.contrib.auth import get_user_model
        User = get_user_model()

        applied = 0
        for profile in queryset:
            users = User.objects.filter(
                website=profile.website,
                is_active=True,
            )
            user_ids = list(users.values_list('id', flat=True))
            result = NotificationProfileService.apply_profile_to_users(
                profile=profile,
                website=profile.website,
                user_ids=user_ids,
                override_existing=False,
            )
            applied += result.get('applied', 0)
        self.message_user(request, f"Applied profile to {applied} user(s).")


# ─────────────────────────────────────────────────────────────
# Broadcasts
# ─────────────────────────────────────────────────────────────

@admin.register(BroadcastNotification)
class BroadcastNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'website', 'is_active',
        'is_blocking', 'require_acknowledgement',
        'pinned', 'scheduled_for', 'sent_at',
        'expires_at', 'created_at',
    )
    list_filter = (
        'website', 'is_active', 'pinned',
        'is_blocking', 'require_acknowledgement',
    )
    search_fields = ('title', 'message')
    readonly_fields = ('sent_at', 'created_at', 'updated_at')

    actions = ['cancel_broadcasts']

    @admin.action(description='Cancel selected broadcasts')
    def cancel_broadcasts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Cancelled {updated} broadcast(s).")


@admin.register(BroadcastOverride)
class BroadcastOverrideAdmin(admin.ModelAdmin):
    list_display = ('broadcast', 'user', 'website', 'is_active')
    search_fields = ('website__domain', 'user__email')
    list_filter = ('website', 'is_active')
    readonly_fields = ('created_at',)


# ─────────────────────────────────────────────────────────────
# Digests
# ─────────────────────────────────────────────────────────────

@admin.register(NotificationDigest)
class NotificationDigestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event_key', 'digest_group',
        'category', 'priority',
        'is_sent', 'is_read', 'is_critical',
        'scheduled_for', 'sent_at', 'created_at',
    )
    list_filter = ('is_sent', 'is_read', 'is_critical', 'category')
    search_fields = ('event_key', 'digest_group')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'sent_at')


# ─────────────────────────────────────────────────────────────
# Notification groups
# ─────────────────────────────────────────────────────────────

@admin.register(NotificationGroup)
class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'default_channel',
        'default_priority', 'is_enabled_by_default',
    )
    search_fields = ('name',)


# ─────────────────────────────────────────────────────────────
# Global settings
# ─────────────────────────────────────────────────────────────

class GlobalNotificationSystemSettingsForm(forms.ModelForm):
    class Meta:
        model = GlobalNotificationSystemSettings
        fields = '__all__'
        widgets = {
            'email_provider_config': AdminTextareaWidget(
                attrs={'rows': 10, 'cols': 80}
            ),
        }

    def clean_email_provider_config(self):
        data = self.cleaned_data.get('email_provider_config', {})
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError as exc:
                raise ValidationError(
                    f"Invalid JSON: {exc}"
                ) from exc
        return data


@admin.register(GlobalNotificationSystemSettings)
class GlobalNotificationSystemSettingsAdmin(admin.ModelAdmin):
    form = GlobalNotificationSystemSettingsForm
    list_display = (
        'website',
        'email_provider', 'email_from_name',
        'email_from_address', 'email_noreply_address',
        'email_enabled', 'in_app_enabled',
    )
    search_fields = ('website__domain', 'email_from_address')
    list_filter = ('email_provider', 'email_enabled', 'in_app_enabled')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Website', {
            'fields': ('website',),
        }),
        ('Email provider', {
            'fields': (
                'email_provider',
                'email_provider_config',
                'email_from_name',
                'email_from_address',
                'email_noreply_address',
                'email_reply_to',
            ),
        }),
        ('Channel toggles', {
            'fields': ('email_enabled', 'in_app_enabled'),
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )