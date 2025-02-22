from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'status', 'created_at', 'website')
    search_fields = ('user__username', 'title', 'message')
    list_filter = ('type', 'is_read', 'status', 'website')
    ordering = ('-created_at',)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'receive_email', 'receive_sms', 'receive_push', 'receive_in_app', 'website')
    search_fields = ('user__username',)
    list_filter = ('website',)