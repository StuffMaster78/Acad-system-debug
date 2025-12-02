"""
Serializers for Ticket SLA
"""
from rest_framework import serializers
from tickets.sla_timers import TicketSLA


class TicketSLASerializer(serializers.ModelSerializer):
    """Serializer for ticket SLA tracking."""
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)
    ticket_status = serializers.CharField(source='ticket.status', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    first_response_time_remaining = serializers.SerializerMethodField()
    is_urgent = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketSLA
        fields = [
            'id', 'ticket', 'ticket_title', 'ticket_status',
            'website', 'created_at', 'priority',
            'first_response_deadline', 'resolution_deadline',
            'first_response_at', 'resolved_at',
            'first_response_breached', 'resolution_breached',
            'time_remaining', 'first_response_time_remaining',
            'is_urgent', 'is_overdue'
        ]
        read_only_fields = [
            'id', 'created_at', 'first_response_at', 'resolved_at',
            'first_response_breached', 'resolution_breached'
        ]
    
    def get_time_remaining(self, obj):
        """Get time remaining until resolution deadline."""
        return obj.get_time_remaining()
    
    def get_first_response_time_remaining(self, obj):
        """Get time remaining until first response deadline."""
        return obj.get_first_response_time_remaining()
    
    def get_is_urgent(self, obj):
        """Check if SLA is urgent (less than 1 hour remaining)."""
        time_remaining = obj.get_time_remaining()
        if time_remaining:
            return time_remaining.get('is_urgent', False)
        return False
    
    def get_is_overdue(self, obj):
        """Check if SLA is overdue."""
        time_remaining = obj.get_time_remaining()
        if time_remaining:
            return time_remaining.get('is_overdue', False)
        return obj.resolution_breached


class TicketSLACreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket SLA (usually auto-created)."""
    
    class Meta:
        model = TicketSLA
        fields = ['ticket']


class TicketSLAMarkFirstResponseSerializer(serializers.Serializer):
    """Serializer for marking first response."""
    pass  # No fields needed, just triggers the action


class TicketSLAMarkResolvedSerializer(serializers.Serializer):
    """Serializer for marking ticket as resolved."""
    pass  # No fields needed, just triggers the action

