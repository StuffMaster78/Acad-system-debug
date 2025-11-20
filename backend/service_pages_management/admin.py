from django.contrib import admin
from .models import ServicePage
from .models.pdf_samples import (
    ServicePagePDFSampleSection, ServicePagePDFSample, ServicePagePDFSampleDownload
)


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    """
    Admin configuration for service pages.
    """
    list_display = ('title', 'website', 'is_published', 'publish_date')
    list_filter = ('website', 'is_published')
    search_fields = ('title', 'slug', 'header')


# Service Page PDF Sample Admin
@admin.register(ServicePagePDFSampleSection)
class ServicePagePDFSampleSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "service_page", "display_order", "is_active", "requires_auth", "pdf_samples_count")
    search_fields = ("title", "description", "service_page__title")
    list_filter = ("is_active", "requires_auth", "service_page__website")
    ordering = ("service_page", "display_order")
    
    def pdf_samples_count(self, obj):
        return obj.pdf_samples.filter(is_active=True).count()
    pdf_samples_count.short_description = "Active PDFs"


@admin.register(ServicePagePDFSample)
class ServicePagePDFSampleAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "file_size_human", "download_count", "is_featured", "is_active", "uploaded_by")
    search_fields = ("title", "description", "section__title", "section__service_page__title")
    list_filter = ("is_active", "is_featured", "section__service_page__website", "created_at")
    readonly_fields = ("file_size", "file_size_human", "download_count", "uploaded_by", "created_at", "updated_at")
    ordering = ("section", "is_featured", "display_order")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("section", "title", "description", "pdf_file")
        }),
        ("Display", {
            "fields": ("display_order", "is_featured", "is_active")
        }),
        ("Analytics", {
            "fields": ("file_size", "file_size_human", "download_count")
        }),
        ("Metadata", {
            "fields": ("uploaded_by", "created_at", "updated_at")
        }),
    )
    
    def file_size_human(self, obj):
        """Display human-readable file size."""
        if not obj or not obj.file_size:
            return "Unknown"
        
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_human.short_description = "File Size"


@admin.register(ServicePagePDFSampleDownload)
class ServicePagePDFSampleDownloadAdmin(admin.ModelAdmin):
    list_display = ("pdf_sample", "user", "ip_address", "downloaded_at")
    search_fields = ("pdf_sample__title", "user__username", "ip_address")
    list_filter = ("downloaded_at", "pdf_sample__section__service_page__website")
    readonly_fields = ("downloaded_at",)
    ordering = ("-downloaded_at",)
    
    def has_add_permission(self, request):
        return False
