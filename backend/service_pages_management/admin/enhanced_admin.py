"""
Enhanced admin interface for service pages with SEO, FAQs, Resources, CTAs.
"""
from django.contrib import admin
from ..models.enhanced_models import (
    ServicePageFAQ, ServicePageResource, ServicePageCTA,
    ServicePageSEOMetadata, ServicePageEditHistory
)


@admin.register(ServicePageFAQ)
class ServicePageFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "service_page", "is_featured", "display_order", "upvote_count")
    search_fields = ("question", "answer")
    list_filter = ("is_featured", "accepted_answer", "service_page__website")
    ordering = ("service_page", "is_featured", "display_order")


@admin.register(ServicePageResource)
class ServicePageResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "service_page", "resource_type", "display_order")
    search_fields = ("title", "url", "description")
    list_filter = ("resource_type", "service_page__website")
    ordering = ("service_page", "display_order")


@admin.register(ServicePageCTA)
class ServicePageCTAAdmin(admin.ModelAdmin):
    list_display = ("title", "service_page", "style", "is_active", "display_order")
    search_fields = ("title", "description", "button_text")
    list_filter = ("style", "is_active", "service_page__website")
    ordering = ("service_page", "display_order")


@admin.register(ServicePageSEOMetadata)
class ServicePageSEOMetadataAdmin(admin.ModelAdmin):
    list_display = ("service_page", "article_type", "has_og_image", "has_twitter_image")
    search_fields = ("service_page__title", "keywords", "og_title", "twitter_title")
    list_filter = ("article_type", "service_page__website")
    
    fieldsets = (
        ("Page Reference", {
            "fields": ("service_page",)
        }),
        ("Schema.org", {
            "fields": ("keywords", "article_type", "schema_breadcrumb", "schema_organization", "schema_rating")
        }),
        ("Open Graph", {
            "fields": ("og_type", "og_title", "og_description", "og_image", "og_url", "og_site_name")
        }),
        ("Twitter Card", {
            "fields": ("twitter_card_type", "twitter_title", "twitter_description", "twitter_image", "twitter_site")
        }),
        ("Additional", {
            "fields": ("google_business_url", "canonical_url")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
    readonly_fields = ("created_at", "updated_at")
    
    def has_og_image(self, obj):
        return bool(obj.og_image)
    has_og_image.boolean = True
    has_og_image.short_description = "OG Image"
    
    def has_twitter_image(self, obj):
        return bool(obj.twitter_image)
    has_twitter_image.boolean = True
    has_twitter_image.short_description = "Twitter Image"


@admin.register(ServicePageEditHistory)
class ServicePageEditHistoryAdmin(admin.ModelAdmin):
    list_display = ("service_page", "edited_by", "edited_at", "changes_summary")
    search_fields = ("service_page__title", "edited_by__username", "changes_summary")
    list_filter = ("edited_at", "service_page__website")
    readonly_fields = ("edited_at",)
    ordering = ("-edited_at",)

