from django.contrib import admin
from .models import Ticket, TicketMessage


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'recipient', 'status', 'category', 'is_escalated', 'created_at']
    list_filter = ['status', 'category', 'is_escalated', 'website']
    search_fields = ['title', 'created_by__email', 'recipient__email', 'description']
    ordering = ['-created_at']


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'sender', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['ticket__title', 'sender__email', 'message']