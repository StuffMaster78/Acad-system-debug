from django.contrib import admin
from .models import QAChecklistItem, QAChecklistResult, QAChecklistTemplate


class QAChecklistItemInline(admin.TabularInline):
    model = QAChecklistItem
    extra = 3
    fields = ["category", "text", "is_required", "display_order"]


@admin.register(QAChecklistTemplate)
class QAChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "website", "is_active", "is_default", "created_at"]
    list_filter = ["is_active", "is_default", "website"]
    search_fields = ["name", "description"]
    inlines = [QAChecklistItemInline]
    readonly_fields = ["created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(QAChecklistResult)
class QAChecklistResultAdmin(admin.ModelAdmin):
    list_display = ["order", "template", "reviewer", "verdict", "pass_rate", "completed_at"]
    list_filter = ["verdict", "template"]
    readonly_fields = ["created_at", "updated_at", "pass_rate"]
    search_fields = ["order__topic", "notes"]
