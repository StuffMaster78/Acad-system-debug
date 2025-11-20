from django.contrib import admin
from class_management.models import ExpressClass


@admin.register(ExpressClass)
class ExpressClassAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'website', 'course', 'discipline', 
        'status', 'price', 'assigned_writer', 'created_at'
    )
    list_filter = ('status', 'website', 'academic_level', 'created_at')
    search_fields = ('client__username', 'client__email', 'course', 'institution', 'discipline')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('client', 'website', 'status', 'assigned_writer')
        }),
        ('Class Details', {
            'fields': (
                'start_date', 'end_date', 'discipline', 'institution', 
                'course', 'academic_level'
            )
        }),
        ('Workload', {
            'fields': (
                'number_of_discussion_posts', 'number_of_discussion_posts_replies',
                'number_of_assignments', 'number_of_exams', 'number_of_quizzes',
                'number_of_projects', 'number_of_presentations', 'number_of_papers',
                'total_workload_in_pages'
            )
        }),
        ('Pricing', {
            'fields': ('price', 'price_approved', 'installments_needed')
        }),
        ('School Login', {
            'fields': ('school_login_link', 'school_login_username', 'school_login_password')
        }),
        ('Admin Review', {
            'fields': (
                'scope_review_notes', 'admin_notes', 
                'reviewed_by', 'reviewed_at'
            )
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'is_complete')
        }),
    )
