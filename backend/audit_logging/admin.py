from django.contrib import admin
from audit_logging.models import AuditLogEntry as AuditLog
from audit_logging.models import WebhookAuditLog
from django.utils.translation import gettext_lazy as _
# from audit_logging.models import AuditLogEntry

# @admin.register(AuditLogEntry)
# class AuditLogEntryAdmin(admin.ModelAdmin):
#     list_display = ('action', 'actor', 'target', 'target_id', 'created_at')
#     search_fields = ('action', 'actor__username', 'target', 'target_id')
#     list_filter = ('action', 'created_at')
#     readonly_fields = ('id', 'created_at', 'ip_address', 'user_agent')

#     fieldsets = (
#         (None, {
#             'fields': ('id', 'action', 'actor', 'target', 'target_id')
#         }),
#         (_('Metadata'), {
#             'fields': ('metadata',)
#         }),
#         (_('Request Info'), {
#             'fields': ('ip_address', 'user_agent')
#         }),
#         (_('Timestamps'), {
#             'fields': ('created_at',)
#         }),
#     )
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