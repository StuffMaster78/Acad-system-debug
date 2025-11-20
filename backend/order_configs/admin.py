from django.contrib import admin
from .models import (
    PaperType, FormattingandCitationStyle, Subject, TypeOfWork, 
    EnglishType, WriterDeadlineConfig, EditingRequirementConfig
)


@admin.register(PaperType)
class PaperTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    list_filter = ['website']


@admin.register(FormattingandCitationStyle)
class FormattingStyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    list_filter = ['website']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'is_technical']
    search_fields = ['name']
    list_filter = ['website', 'is_technical']


@admin.register(TypeOfWork)
class TypeOfWorkAdmin(admin.ModelAdmin):
    list_display = ['name', 'website']
    search_fields = ['name']
    list_filter = ['website']


@admin.register(EnglishType)
class EnglishTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'code']
    search_fields = ['name', 'code']
    list_filter = ['website']


@admin.register(WriterDeadlineConfig)
class WriterDeadlineConfigAdmin(admin.ModelAdmin):
    list_display = ['writer_deadline_percentage', 'website']
    search_fields = ['website__name']
    list_filter = ['website']


@admin.register(EditingRequirementConfig)
class EditingRequirementConfigAdmin(admin.ModelAdmin):
    list_display = [
        'website', 'enable_editing_by_default', 'skip_editing_for_urgent',
        'allow_editing_for_early_submissions', 'created_by', 'created_at'
    ]
    search_fields = ['website__domain', 'website__name']
    list_filter = [
        'enable_editing_by_default', 'skip_editing_for_urgent',
        'allow_editing_for_early_submissions', 'editing_required_for_first_orders',
        'editing_required_for_high_value', 'created_at'
    ]
    fieldsets = (
        ('Website', {
            'fields': ('website',)
        }),
        ('General Settings', {
            'fields': (
                'enable_editing_by_default',
                'skip_editing_for_urgent',
            )
        }),
        ('Early Submission Settings', {
            'fields': (
                'allow_editing_for_early_submissions',
                'early_submission_hours_threshold',
            )
        }),
        ('Special Requirements', {
            'fields': (
                'editing_required_for_first_orders',
                'editing_required_for_high_value',
                'high_value_threshold',
            )
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)