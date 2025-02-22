from django.contrib import admin
from .models import Ticket, TicketMessage, TicketLog, TicketStatistics

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
