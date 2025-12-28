from django.contrib import admin
from .models import Website, WebsiteStaticPage, WebsiteSettings, WebsiteTermsAcceptance, ExternalReviewLink
from .models_integrations import WebsiteIntegrationConfig
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Q
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
class SoftDeleteFilter(SimpleListFilter):
    """Filter to show soft-deleted items."""
    title = _('Soft Deleted')
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return (
            (True, _('Yes')),
            (False, _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(is_deleted=self.value() == 'True')
    

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
        ("Communication Widgets", {
            "fields": ("enable_live_chat", "communication_widget_type", "tawkto_widget_id", "tawkto_property_id", "communication_widget_config"),
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
    list_display = ("title", "website", "language", "version", "last_updated")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name="Admin").exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    

# website/admin.py
# class WebsiteSettingsInline(admin.TabularInline):
#     model = WebsiteSettings
#     extra = 1  # Only show one inline form for the website settings

# class WebsiteAdmin(admin.ModelAdmin):
#     inlines = [WebsiteSettingsInline]

admin.site.register(WebsiteSettings)  # assuming you don't have a custom admin
admin.site.register(WebsiteStaticPage, WebsiteStaticPageAdmin)


@admin.register(WebsiteTermsAcceptance)
class WebsiteTermsAcceptanceAdmin(admin.ModelAdmin):
    list_display = ("user", "website", "static_page", "terms_version", "accepted_at")
    list_filter = ("website", "terms_version")
    search_fields = ("user__email", "user__username", "website__name", "website__domain")


@admin.register(WebsiteIntegrationConfig)
class WebsiteIntegrationConfigAdmin(admin.ModelAdmin):
    """Admin interface for managing website integration configurations."""
    
    list_display = (
        "website", "integration_type", "name", "is_active",
        "created_at", "updated_at", "created_by"
    )
    list_filter = (
        "integration_type", "is_active", "website", "created_at"
    )
    search_fields = (
        "website__name", "website__domain", "name", "description",
        "integration_type"
    )
    readonly_fields = ("created_at", "updated_at", "created_by")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("website", "integration_type", "name", "description", "is_active")
        }),
        ("Credentials (Encrypted)", {
            "fields": ("encrypted_api_key", "encrypted_secret_key", "encrypted_access_token"),
            "description": "These fields store encrypted credentials. Use the API or frontend to set values."
        }),
        ("Configuration", {
            "fields": ("config",),
            "description": "JSON configuration for endpoints, regions, and other settings."
        }),
        ("Metadata", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by on first save."""
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ExternalReviewLink)
class ExternalReviewLinkAdmin(admin.ModelAdmin):
    """Admin interface for managing external review links (TrustPilot, Google Reviews, etc.)."""
    
    list_display = (
        "review_site_name", "website", "review_type", "is_active",
        "display_order", "created_at", "updated_at"
    )
    list_filter = (
        "review_type", "is_active", "website", "created_at"
    )
    search_fields = (
        "review_site_name", "website__name", "website__domain", "review_url", "description"
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("website", "display_order", "review_site_name")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("website", "review_site_name", "review_url", "review_type", "is_active")
        }),
        ("Display Settings", {
            "fields": ("display_order", "description", "icon_url"),
            "description": "Control how this review link is displayed to clients."
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('website')