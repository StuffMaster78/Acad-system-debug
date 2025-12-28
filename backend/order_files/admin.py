from django.contrib import admin
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink,
    ExtraServiceFile, OrderFilesConfig, OrderFileCategory, StyleReferenceFile
)

@admin.register(OrderFilesConfig)
class OrderFilesConfigAdmin(admin.ModelAdmin):
    list_display = ["allowed_extensions", "enable_external_links", "max_upload_size"]
    list_editable = ["enable_external_links", "max_upload_size"]

@admin.register(OrderFileCategory)
class OrderFileCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "website", "is_universal", "is_final_draft", "is_extra_service", "allowed_extensions"]
    list_filter = ["website", "is_final_draft", "is_extra_service"]
    search_fields = ["name"]
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "website", "allowed_extensions")
        }),
        ("Category Type", {
            "fields": ("is_final_draft", "is_extra_service"),
            "description": "Mark if this is a Final Draft category or Extra Service category"
        }),
    )
    
    def is_universal(self, obj):
        """Display if this is a universal category"""
        return "Yes" if obj.website is None else "No"
    is_universal.short_description = "Universal"
    is_universal.boolean = True

@admin.register(OrderFile)
class OrderFileAdmin(admin.ModelAdmin):
    list_display = ["order", "category", "uploaded_by", "created_at", "is_downloadable"]
    list_filter = ["category", "is_downloadable"]
    search_fields = ["order__id", "uploaded_by__username"]

@admin.register(FileDeletionRequest)
class FileDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ["file", "requested_by", "status", "requested_at"]
    list_filter = ["status"]
    search_fields = ["file__order__id", "requested_by__username"]

@admin.register(ExternalFileLink)
class ExternalFileLinkAdmin(admin.ModelAdmin):
    list_display = ["order", "uploaded_by", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["order__id", "uploaded_by__username"]

@admin.register(ExtraServiceFile)
class ExtraServiceFileAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "order", "uploaded_by", "created_at", "is_downloadable"]
    list_filter = []
    search_fields = ["order__id", "uploaded_by__username"]

@admin.register(StyleReferenceFile)
class StyleReferenceFileAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "reference_type", "uploaded_by", "file_name", "uploaded_at", "is_visible_to_writer"]
    list_filter = ["reference_type", "is_visible_to_writer", "uploaded_at"]
    search_fields = ["order__id", "order__topic", "uploaded_by__username", "file_name", "description"]
    readonly_fields = ["uploaded_at", "file_size"]