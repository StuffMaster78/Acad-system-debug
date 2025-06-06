from django.contrib import admin
from .models import (
    Ticket, TicketMessage, TicketLog,
    TicketStatistics, TicketAttachment
)

# Admin for Ticket
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'is_escalated', 'created_by', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'category', 'is_escalated')
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority', 'assigned_to', 'is_escalated']
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

admin.site.register(Ticket, TicketAdmin)

# Admin for TicketMessage
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'is_internal', 'created_at')
    list_filter = ('is_internal',)
    search_fields = ['message']
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(TicketMessage, TicketMessageAdmin)

# Admin for TicketLog
class TicketLogAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'action', 'performed_by', 'timestamp')
    list_filter = ('action',)
    search_fields = ['action']
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

admin.site.register(TicketLog, TicketLogAdmin)

# Admin for TicketStatistics
class TicketStatisticsAdmin(admin.ModelAdmin):
    list_display = ('website', 'total_tickets', 'resolved_tickets', 'avg_resolution_time', 'created_at')
    list_filter = ('website',)
    search_fields = ['website__name']
    readonly_fields = ('total_tickets', 'resolved_tickets', 'avg_resolution_time', 'created_at')
    ordering = ('-created_at',)

    def avg_resolution_time(self, obj):
        return obj.calculate_avg_resolution_time() 

admin.site.register(TicketStatistics, TicketStatisticsAdmin)

@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'uploaded_by', 'uploaded_at')
    list_filter = ('ticket', 'uploaded_by')
    search_fields = ['ticket__title', 'uploaded_by__username']
    readonly_fields = ('uploaded_at',)
    ordering = ('-uploaded_at',)
    def uploaded_at(self, obj):
        return obj.created_at
    uploaded_at.admin_order_field = 'created_at'
    uploaded_at.short_description = 'Uploaded At'
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('ticket', 'uploaded_by')
        return self.readonly_fields
    def has_add_permission(self, request, obj=None):
        return request.user.is_staff or request.user.groups.filter(name="Support").exists()
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.groups.filter(name="Support").exists()
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff or request.user.groups.filter(name="Support").exists()
    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.groups.filter(name="Support").exists()
    def has_module_permission(self, request):
        return request.user.is_staff or request.user.groups.filter(name="Support").exists()
# Register the TicketAttachment model with the custom admin class
admin.site.register(TicketAttachment, TicketAttachmentAdmin)



