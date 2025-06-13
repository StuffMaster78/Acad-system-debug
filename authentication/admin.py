from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin.sites import NotRegistered

from authentication.models.mfa_settings import MFASettings
from authentication.models.sessions import UserSession
from authentication.models.tokens import SecureToken
from authentication.models.register import RegistrationToken
from authentication.models.backup_code import BackupCode
from authentication.models.audit import AuditLog

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    """
    Custom user admin interface with support for MFA and other custom fields.
    """
    list_display = UserAdmin.list_display + ('is_active', 'is_staff')
    inlines = []


@admin.register(MFASettings)
class MFASettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing MFA settings for users.
    """
    list_display = (
        'user', 'is_mfa_enabled', 'mfa_method',
        'mfa_phone_number', 'mfa_email_verified'
    )
    search_fields = ('user__email', 'mfa_method')
    list_filter = ('is_mfa_enabled', 'mfa_method')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id", "event", "linked_user", "ip_address", "device",
        "location", "created_at", "highlighted",
    )
    list_filter = ("event", "created_at")
    search_fields = ("event", "user__email", "ip_address", "device", "location")
    ordering = ("-created_at",)

    def linked_user(self, obj):
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return "Anonymous"

    def highlighted(self, obj):
        event = obj.event.lower()
        if event.startswith("failed"):
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>', obj.event
            )
        elif event.startswith("success"):
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>', obj.event
            )
        return obj.event

    linked_user.short_description = "User"
    highlighted.short_description = "Event (highlighted)"


@admin.register(SecureToken)
class SecureTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'purpose', 'is_active', 'created_at', 'expires_at'
    )
    list_filter = ('purpose', 'is_active')
    search_fields = ('user__email',)
    ordering = ('-created_at',)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'session_key', 'ip_address', 'device_type',
        'created_at', 'last_activity', 'expires_at', 'is_active'
    )
    search_fields = ('user__email', 'ip_address', 'device_type', 'session_key')
    list_filter = ('is_active',)
    ordering = ('-last_activity',)


@admin.register(BackupCode)
class BackupCodeAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'used', 'created_at', 'used_at'
    )
    search_fields = ('user__email',)
    list_filter = ('used',)


@admin.register(RegistrationToken)
class RegistrationTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'token', 'is_used', 'created_at', 'expires_at'
    )
    search_fields = ('user__email', 'token')
    list_filter = ('is_used',)


# Unregister default User if needed, then register our custom admin
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
