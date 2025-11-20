"""
Serializers for writer progress reports.
"""
from rest_framework import serializers
from orders.models import WriterProgress
from users.serializers import SimpleUserSerializer


class WriterProgressSerializer(serializers.ModelSerializer):
    """Serializer for writer progress reports."""
    writer = SimpleUserSerializer(read_only=True)
    withdrawn_by = SimpleUserSerializer(read_only=True)
    writer_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = WriterProgress
        fields = [
            'id', 'order', 'writer', 'writer_id', 'progress_percentage', 
            'notes', 'is_withdrawn', 'withdrawn_by', 'withdrawn_at', 
            'withdrawal_reason', 'contains_screened_words', 'timestamp', 'updated_at'
        ]
        read_only_fields = [
            'id', 'writer', 'is_withdrawn', 'withdrawn_by', 'withdrawn_at',
            'withdrawal_reason', 'contains_screened_words', 'timestamp', 'updated_at'
        ]
    
    def validate_progress_percentage(self, value):
        """Ensure progress is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress percentage must be between 0 and 100.")
        return value
    
    def create(self, validated_data):
        """Create a progress report."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User must be authenticated.")
        
        # Set writer from request user
        validated_data['writer'] = request.user
        validated_data['writer_id'] = None  # Remove write_only field
        
        # Get order and set website
        order = validated_data.get('order')
        if order:
            validated_data['website'] = order.website
        
        return super().create(validated_data)


class WriterProgressListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing progress reports."""
    writer = SimpleUserSerializer(read_only=True)
    
    class Meta:
        model = WriterProgress
        fields = [
            'id', 'progress_percentage', 'notes', 'is_withdrawn',
            'contains_screened_words', 'timestamp'
        ]

