from rest_framework import serializers
from django.utils.timezone import now  # Importing now
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'topic', 'instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'pages', 
            'slides', 'resources', 'spacing', 'deadline', 'writer_deadline', 
            'client', 'writer', 'preferred_writer', 'total_cost', 
            'writer_compensation', 'extra_services', 'subject', 'discount_code', 
            'is_paid', 'status', 'flag', 'created_at', 'updated_at', 
            'created_by_admin', 'is_special_order'
        ]
        read_only_fields = [
            'id', 'total_cost', 'writer_compensation', 'is_paid', 
            'created_at', 'updated_at', 'flag', 'writer_deadline'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'topic', 'instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'pages', 
            'slides', 'resources', 'spacing', 'deadline', 'extra_services', 
            'discount_code', 'client', 'preferred_writer'
        ]

    def validate_deadline(self, value):
        """
        Ensure the deadline is in the future.
        """
        if value <= now():
            raise serializers.ValidationError("The deadline must be in the future.")
        return value