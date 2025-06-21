from django.contrib import admin
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink,
    ExtraServiceFile, OrderFilesConfig, OrderFileCategory
)

@admin.register(OrderFilesConfig)
class OrderFilesConfigAdmin(admin.ModelAdmin):
    list_display = ["allowed_extensions", "enable_external_links", "max_upload_size"]
    list_editable = ["enable_external_links", "max_upload_size"]

@admin.register(OrderFileCategory)
class OrderFileCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_final_draft", "is_extra_service"]

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