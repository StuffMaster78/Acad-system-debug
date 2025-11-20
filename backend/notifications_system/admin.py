from django.contrib import admin

from notifications_system.services.preferences import NotificationPreferenceResolver
from notifications_system.models.notifications import Notification
from notifications_system.models.notification_preferences import (
    NotificationPreference, EventNotificationPreference,
    RoleNotificationPreference, UserNotificationPreference,
    NotificationEventPreference, NotificationPreferenceGroup,
    NotificationPreferenceProfile,
)
from notifications_system.models.broadcast_notification import (
    BroadcastNotification, BroadcastOverride
)
from notifications_system.models.notification_profile import (
    NotificationProfile, NotificationGroupProfile,
    GroupNotificationProfile
)
from notifications_system.models.notification_event import NotificationEvent

from notifications_system.models.notification_group import NotificationGroup
from notifications_system.models.notification_settings import UserNotificationSettings
from notifications_system.utils.email_helpers import send_priority_email

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from authentication.models.login import LoginSession
from authentication.models.logout import LogoutEvent
import json
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django import forms
from notifications_system.utils.email_helpers import send_priority_email
from notifications_system.models.event_config import NotificationEventConfig
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from notifications_system.models.notification_event_override import NotificationEventOverride
from notifications_system.registry.notification_event_loader import load_event_configs
from notifications_system.registry.validator import validate_event_config
from django.core.exceptions import ValidationError

from .models.notifications_user_status import NotificationsUserStatus
from .models.delivery import Delivery
from .models.outbox import Outbox
from .models.notifications_template import NotificationTemplate

@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["website", "user", "channel"]
    list_filter = ["website", "channel"]
    search_fields = ["user__email", "user__username"]

admin.register(NotificationPreferenceGroup)
class NotificationPreferenceGroup(admin.ModelAdmin):
    list_display = ("website", "name", "description", "default_channels", "is_active", "quiet_hours")
    list_filter = ("website", "is_active")
    search_fields = ("name", "description", "quiet_hours")

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("event", "channel", "website", "locale", "version")
    list_filter = ("channel", "website", "locale")
    search_fields = ("event__key",)
    autocomplete_fields = ("event", "website")

# @admin.register(UserPreference)
# class UserPreferenceAdmin(admin.ModelAdmin):
#     list_display = ("user", "website", "channel", "enabled")
#     list_filter = ("channel", "enabled", "website")
#     search_fields = ("user__email", "user__username")
#     autocomplete_fields = ("user", "website")

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "event_key", "user", "channel", "status",
        "priority", "attempts", "queued_at", "sent_at",
    )
    list_filter = ("status", "channel", "priority")
    search_fields = ("event_key", "user__email")
    date_hierarchy = "queued_at"
    autocomplete_fields = ("user", "website")

@admin.register(Outbox)
class OutboxAdmin(admin.ModelAdmin):
    list_display = ("id", "event_key", "user", "attempts", "processed_at")
    list_filter = ("processed_at",)
    search_fields = ("event_key", "user__email")
    autocomplete_fields = ("user", "website")
class UserNotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = UserNotificationSettings
        fields = '__all__'
        widgets = {
            'fallback_rules': AdminTextareaWidget(attrs={'rows': 10, 'cols': 80}),
            'max_retries_per_channel': AdminTextareaWidget(attrs={'rows': 5, 'cols': 80}),
        }

    def clean_fallback_rules(self):
        import json
        data = self.cleaned_data["fallback_rules"]
        if isinstance(data, str):
            return json.loads(data)
        return data

    def clean_max_retries_per_channel(self):
        import json
        data = self.cleaned_data["max_retries_per_channel"]
        if isinstance(data, str):
            return json.loads(data)
        return data

@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    form = UserNotificationSettingsForm


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "is_active", "website", "key", "label", "priority", "enabled", "schema_version")
    list_filter = ("enabled", "priority", "website", "is_active")
    search_fields = ("key", "label", "event", "name")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('website')
    
@admin.register(NotificationPreferenceProfile)
class NotificationPreferenceProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "default_email", "default_sms", "default_push", "default_in_app")
    search_fields = ("name", "website__domain")
    list_filter = ("website",)

@admin.register(BroadcastOverride)
class BroadcastOverrideAdmin(admin.ModelAdmin):
    """Admin for BroadcastOverride model."""
    list_display = ("broadcast", "website", "is_active")
    search_fields = ("website__domain",)
    list_filter = ("website",)


@admin.register(NotificationGroup)
class NotificationGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "default_channel", "default_priority", "is_enabled_by_default")
    search_fields = ("name",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'type', 
        'event', 'title', 'is_read', 'is_sent',
        'sent_at', 'status', 'created_at',
        'website', 'short_message'
    )
    search_fields = (
        'user__username', 'user__email',
        'payload', 'category', 'title', 'message'
    )
    list_filter = (
        'category', 'priority', 'type', 'is_read',
        'sent_at', 'event', 'status', 'is_sent',
        'website', 'channels'
    )
    readonly_fields = (
        "user",
        "event",
        "category",
        "priority",
        "payload_pretty",
        "is_read",
        "is_sent",
        "sent_at",
        "channels",
        "website",
        "actor",
        "created_at",
        "updated_at",
    )
    ordering = ('-created_at',)

    actions = [
        "mark_as_read",
        "mark_as_sent",
        "delete_failed_notifications",
    ]

    def short_message(self, obj):
        try:
            return obj.payload.get("message", "")[:50]
        except Exception:
            return "-"
    short_message.short_description = "Message"

    def payload_pretty(self, obj):
        try:
            data = json.dumps(obj.payload, indent=2)
            return format_html(f"<pre style='max-width: 600px;'>{data}</pre>")
        except Exception:
            return str(obj.payload)
    payload_pretty.short_description = "Payload"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected as read"

    def mark_as_sent(self, request, queryset):
        updated = queryset.update(is_sent=True)
        self.message_user(request, f"{updated} notification(s) marked as sent.")
    mark_as_sent.short_description = "Mark selected as sent"

    def delete_failed_notifications(self, request, queryset):
        failed = queryset.filter(is_sent=False)
        count = failed.count()
        failed.delete()
        self.message_user(request, f"{count} failed notification(s) deleted.")
    delete_failed_notifications.short_description = "Delete failed notifications"

@admin.register(NotificationProfile)
class NotificationProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "default_email", "default_sms", "default_push", "default_in_app", "dnd_start", "dnd_end")
    list_filter = ("default_email", "default_in_app")

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'email_enabled', 'sms_enabled',
        'push_enabled', 'in_app_enabled', 'website',
        'mute_all', 'digest_only', 'updated_at',
        'created_at'
    )
    search_fields = ('user__username', 'website__domain')
    list_filter = (
        'website', 'mute_all', 'digest_only', 'receive_email',
        'receive_sms', 'receive_push', 'receive_in_app'
    )

@admin.register(EventNotificationPreference)
class EventNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "website", "email_enabled", "sms_enabled",  "push_enabled", "in_app_enabled")
    list_filter = ("event", "website", "email_enabled", "push_enabled", "sms_enabled", "in_app_enabled")
    search_fields = ("user__username", "user__email")


@admin.register(NotificationGroupProfile)
class NotificationGroupProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name", "website", "group", "profile",
        "allowed_channels", "min_priority", "is_active",
        "created_at", "updated_at"
    )
    # filter_horizontal = ("users", "roles")
    search_fields = ("name", "website__domain", "group__name")
    list_filter = ("website", "group")



@admin.register(BroadcastNotification)
class BroadcastNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "website", "send_email", "pinned", "created_at")
    list_filter = ("website", "is_active", "pinned", "send_email")
    search_fields = ("title", "message")


@admin.register(NotificationEventPreference)
class NotificationEventPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "website")

    @admin.action(description="Reset and re-seed preferences")
    def reset_preferences(modeladmin, request, queryset):
        for user in queryset:
            NotificationPreferenceResolver.reset_user_preferences(user)
            NotificationPreferenceResolver.assign_default_preferences(user, user.website)


@admin.register(RoleNotificationPreference)
class RoleNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("role", "website", "min_priority")
    list_filter = ("website", "role")

@admin.register(GroupNotificationProfile)
class GroupNotificationProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "role_slug", "is_default", "receive_email", "receive_push")
    list_filter = ("is_default",)
    search_fields = ("name", "role_slug")

# notifications_system/admin.py

@admin.action(description="Send test email to self")
def send_test_email(modeladmin, request, queryset):
    user = request.user
    for notif in queryset:
        send_priority_email(
            user=user,
            subject=notif.title,
            message=notif.message,
            context={"message": notif.message},
            priority=notif.priority,
            website=notif.website
        )
        modeladmin.message_user(request, f"Test email sent for: {notif.title}")


@admin.register(NotificationEventConfig)
class NotificationEventConfigAdmin(admin.ModelAdmin):
    list_display = ("event_key", "updated_at")
    search_fields = ("event_key",)
    ordering = ("-updated_at",)



@admin.register(NotificationEventOverride)
class NotificationEventOverrideAdmin(admin.ModelAdmin):
    list_display = (
        "event_key",
        "website",
        "enabled",
        "priority",
        "updated_at",
        "schema_valid",
    )
    list_filter = ("website", "enabled")
    search_fields = ("event_key",)

    readonly_fields = ("schema_valid", "full_config_preview")

    fieldsets = (
        (None, {
            "fields": (
                "website",
                "event_key",
                "enabled",
                "priority",
                "channels",
                "roles",
            )
        }),
        ("Template & Fallback", {
            "fields": (
                "template_key",
                "fallback_message",
            )
        }),
        ("Debug & Validation", {
            "classes": ("collapse",),
            "fields": (
                "schema_valid",
                "full_config_preview",
            )
        }),
    )

    def schema_valid(self, obj):
        """
        Returns ✅/❌ depending on whether merged config passes schema validation.
        """
        if not obj:
            return "-"
        try:
            merged = self._get_merged_config(obj)
            validate_event_config({obj.event_key: merged})
            return format_html('<span style="color: green;">✅ Valid</span>')
        except ValidationError as e:
            return format_html('<span style="color: red;">❌ Invalid: {}</span>', str(e))
        except Exception as e:
            return format_html('<span style="color: red;">⚠️ Error: {}</span>', str(e))

    def full_config_preview(self, obj):
        """
        Displays a syntax-highlighted JSON preview of merged event config.
        """
        if not obj:
            return "-"
        try:
            import json
            merged = self._get_merged_config(obj)
            pretty = json.dumps(merged, indent=2)
            return format_html(
                "<pre style='background: #f9f9f9; padding: 10px; border-radius: 4px;'>{}</pre>",
                mark_safe(pretty)
            )
        except Exception as e:
            return f"Error rendering preview: {e}"

    def _get_merged_config(self, obj):
        """
        Load full config for this event_key and override object.
        """
        config = load_event_configs(force_reload=True)
        return config.get(obj.event_key, {})
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Optional: log to your own audit system or console
        print(f"[Admin] Updated NotificationEventOverride: {obj}")



@admin.register(NotificationsUserStatus)
class NotificationsUserStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "notification", "is_read", "pinned", "priority", "created_at")
    list_filter = ("is_read", "pinned", "priority")
    search_fields = ("user__username", "notification__title")