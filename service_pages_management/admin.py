from django.contrib import admin
from .models import ServicePage, ServicePageCategory


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    """
    Admin configuration for service pages.
    """
    list_display = ('title', 'website', 'is_published', 'publish_date')
    list_filter = ('website', 'is_published')
    search_fields = ('title', 'slug', 'header')


@admin.register(ServicePageCategory)
class ServicePageCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for service page categories.
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)
