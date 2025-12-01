"""
Serializers for order templates.
"""
from rest_framework import serializers
from orders.models import OrderTemplate
from orders.serializers import OrderSerializer


class OrderTemplateSerializer(serializers.ModelSerializer):
    """Serializer for order templates."""
    
    paper_type_name = serializers.CharField(source='paper_type.name', read_only=True)
    academic_level_name = serializers.CharField(source='academic_level.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    client_username = serializers.CharField(source='client.username', read_only=True)
    
    class Meta:
        model = OrderTemplate
        fields = [
            'id', 'name', 'description', 'client', 'client_username', 'website',
            'topic', 'paper_type', 'paper_type_name', 'academic_level', 'academic_level_name',
            'subject', 'subject_name', 'number_of_pages', 'order_instructions',
            'additional_services', 'preferred_writer_id', 'preferred_deadline_days',
            'created_at', 'updated_at', 'last_used_at', 'usage_count', 'is_active'
        ]
        read_only_fields = ['client', 'created_at', 'updated_at', 'last_used_at', 'usage_count']


class OrderTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order templates."""
    
    class Meta:
        model = OrderTemplate
        fields = [
            'name', 'description', 'topic', 'paper_type', 'academic_level', 'subject',
            'number_of_pages', 'order_instructions', 'additional_services',
            'preferred_writer_id', 'preferred_deadline_days'
        ]


class OrderFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating order from template."""
    
    template_id = serializers.IntegerField()
    client_deadline = serializers.DateTimeField(required=False)
    writer_deadline = serializers.DateTimeField(required=False)
    custom_instructions = serializers.CharField(required=False, allow_blank=True)
    override_topic = serializers.CharField(required=False, allow_blank=True)
    override_pages = serializers.IntegerField(required=False, min_value=1)

