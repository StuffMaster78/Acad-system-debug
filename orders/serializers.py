from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'title', 'topic', 'instructions', 'academic_level', 
            'type_of_work', 'number_of_pages', 'number_of_slides', 
            'client_deadline', 'writer_deadline', 'client', 'assigned_writer', 
            'total_price', 'additional_services', 'subject', 'discount_code', 'tips', 
            'payment_status', 'status', 'revision_requested', 
            'date_posted', 'completed_at', 'is_high_value', 'is_urgent'
        ]
        read_only_fields = ['id', 'date_posted', 'completed_at']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'title', 'topic', 'instructions', 'academic_level', 
            'type_of_work', 'number_of_pages', 'number_of_slides', 
            'client_deadline', 'additional_services', 'discount_code'
        ]
