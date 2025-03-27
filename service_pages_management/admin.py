from django.contrib import admin
from .models import ServicePage


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    """
    Admin configuration for service pages.
    """
    list_display = ('title', 'website', 'is_published', 'publish_date')
    list_filter = ('website', 'is_published')
    search_fields = ('title', 'slug', 'header')
