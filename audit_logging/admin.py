from django.contrib import admin
from audit_logging.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'app', 'model', 'object_id', 'created_at')
    search_fields = ('user__username', 'action', 'app', 'model', 'object_id', 'message')
    list_filter = ('action', 'app', 'model', 'created_at')