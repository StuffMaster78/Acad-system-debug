from django.contrib import admin
from django.utils import timezone
from .models import ChangelogEntry


@admin.register(ChangelogEntry)
class ChangelogEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "portal_surface", "entry_type", "version", "is_published", "is_pinned", "published_at"]
    list_filter = ["portal_surface", "entry_type", "is_published", "is_pinned", "website"]
    search_fields = ["title", "body", "version"]
    readonly_fields = ["created_at", "updated_at", "created_by"]
    actions = ["publish_entries", "unpublish_entries"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        if obj.is_published and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    @admin.action(description="Publish selected entries")
    def publish_entries(self, request, queryset):
        queryset.filter(published_at__isnull=True).update(published_at=timezone.now())
        queryset.update(is_published=True)

    @admin.action(description="Unpublish selected entries")
    def unpublish_entries(self, request, queryset):
        queryset.update(is_published=False)
