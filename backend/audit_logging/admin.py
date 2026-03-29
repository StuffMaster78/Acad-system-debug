from django.contrib import admin
from audit_logging.models import AuditLogEntry as AuditLog
from audit_logging.models import WebhookAuditLog
from django.utils.translation import gettext_lazy as _

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'created_at')
    search_fields = ('user__username', 'action', 'object_id', 'message')
    list_filter = ('action', 'created_at')

@admin.register(WebhookAuditLog)
class WebhookAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'event', 'platform', 'order_id', 'user',
        'was_successful', 'is_test', 'triggered_at'
    )
    search_fields = ('event', 'user__email', 'webhook_url')
    list_filter = ('platform', 'was_successful', 'is_test')

    readonly_fields = (
        'webhook_url', 'payload',
        'response_body', 'response_status'
    )
    fieldsets = (
        (None, {
            'fields': ('event', 'platform', 'order_id', 'user', 'webhook_url')
        }),
        (_('Payload'), {
            'fields': ('payload',)
        }),
        (_('Response'), {
            'fields': ('response_body', 'response_status', 'was_successful')
        }),
        (_('Metadata'), {
            'fields': ('is_test', 'triggered_at')
        }),
    )