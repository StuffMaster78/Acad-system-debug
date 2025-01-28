from rest_framework import serializers
from .models import Ticket, TicketMessage


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_name', 'message', 'is_internal', 'created_at']
        read_only_fields = ['id', 'sender_name', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.get_full_name", read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_name', 'recipient',
            'recipient_name', 'website', 'status', 'category', 'is_escalated', 
            'created_at', 'updated_at', 'messages'
        ]
        read_only_fields = ['id', 'created_by_name', 'recipient_name', 'created_at', 'updated_at']