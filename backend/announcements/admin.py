"""
Django admin configuration for announcements app.
"""
from django.contrib import admin
from .models import Announcement, AnnouncementView


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin interface for Announcement model."""
    list_display = [
        'id', 'title', 'category', 'is_pinned', 'is_active',
        'view_count', 'created_at'
    ]
    list_filter = ['category', 'created_at', 'broadcast__pinned', 'broadcast__is_active']
    search_fields = ['broadcast__title', 'broadcast__message']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('broadcast', 'category', 'featured_image', 'read_more_url')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at')
        }),
    )

    def title(self, obj):
        return obj.broadcast.title if obj.broadcast else "N/A"
    title.short_description = 'Title'

    def is_pinned(self, obj):
        return obj.broadcast.pinned if obj.broadcast else False
    is_pinned.boolean = True
    is_pinned.short_description = 'Pinned'

    def is_active(self, obj):
        return obj.broadcast.is_active if obj.broadcast else False
    is_active.boolean = True
    is_active.short_description = 'Active'


@admin.register(AnnouncementView)
class AnnouncementViewAdmin(admin.ModelAdmin):
    """Admin interface for AnnouncementView model."""
    list_display = [
        'id', 'user', 'announcement', 'viewed_at',
        'acknowledged', 'acknowledged_at', 'time_spent'
    ]
    list_filter = ['acknowledged', 'viewed_at', 'acknowledged_at']
    search_fields = ['user__email', 'announcement__broadcast__title']
    readonly_fields = ['viewed_at']
    date_hierarchy = 'viewed_at'

