from django.contrib import admin
from .models import Website, WebsiteStaticPage, WebsiteSettings

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    """Admin panel configuration for managing websites."""

    list_display = (
        "name", "domain", "is_active",
        "allow_registration", "allow_guest_checkout",
        "google_analytics_id", "google_search_console_id", "bing_webmaster_id",
        "is_deleted", "deleted_at"
    )
    list_filter = ("is_active", "is_deleted", "allow_registration", "allow_guest_checkout")
    search_fields = ("name", "domain", "google_analytics_id", "google_search_console_id")
    ordering = ("name",)

    fieldsets = (
        ("Basic Details", {
            "fields": ("name", "domain", "slug", "is_active")
        }),
        ("Branding & Contact", {
            "fields": ("logo", "theme_color", "contact_email", "contact_phone"),
            "classes": ("collapse",),  # Makes this section collapsible
        }),
        ("SEO & Analytics", {
            "fields": ("meta_title", "meta_description", "google_analytics_id", "google_search_console_id", "bing_webmaster_id"),
            "classes": ("collapse",),
        }),
        ("Custom Configuration", {
            "fields": ("allow_registration", "allow_guest_checkout"),
        }),
        ("Soft Deletion", {
            "fields": ("is_deleted", "deleted_at"),
            "classes": ("collapse",),  # Makes soft delete info collapsible
        }),
    )

    readonly_fields = ("slug", "deleted_at")  # Slug should not be editable manually

    actions = ["soft_delete_selected", "restore_selected"]

    def soft_delete_selected(self, request, queryset):
        """Soft deletes selected websites."""
        queryset.update(is_deleted=True, deleted_at=timezone.now())
        self.message_user(request, f"{queryset.count()} websites soft-deleted.")

    def restore_selected(self, request, queryset):
        """Restores selected soft-deleted websites."""
        queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, f"{queryset.count()} websites restored.")

    soft_delete_selected.short_description = "Soft delete selected websites"
    restore_selected.short_description = "Restore selected websites"


class WebsiteStaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "website", "last_updated")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name="Admin").exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    

# website/admin.py
class WebsiteSettingsInline(admin.TabularInline):
    model = WebsiteSettings
    extra = 1  # Only show one inline form for the website settings

class WebsiteAdmin(admin.ModelAdmin):
    inlines = [WebsiteSettingsInline]

admin.site.unregister(Website)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(WebsiteSettings)  # assuming you don’t have a custom admin
admin.site.register(WebsiteStaticPage, WebsiteStaticPageAdmin)