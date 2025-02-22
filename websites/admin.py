from django.contrib import admin
from .models import Website

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Website model.
    """
    list_display = ('name', 'domain', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'allow_registration', 'allow_guest_checkout')
    search_fields = ('name', 'domain', 'contact_email', 'contact_phone')
    ordering = ('name',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'domain', 'is_active'),
        }),
        ('Branding', {
            'fields': ('logo', 'theme_color'),
        }),
        ('Contact Details', {
            'fields': ('contact_email', 'contact_phone'),
        }),
        ('SEO Metadata', {
            'fields': ('meta_title', 'meta_description'),
        }),
        ('Custom Configurations', {
            'fields': ('allow_registration', 'allow_guest_checkout'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')