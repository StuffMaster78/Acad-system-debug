"""
Order Drafts Serializers
"""
from rest_framework import serializers
from orders.order_drafts import OrderDraft


class OrderDraftSerializer(serializers.ModelSerializer):
    """Serializer for order drafts."""
    type_of_work_name = serializers.CharField(source='type_of_work.name', read_only=True)
    english_type_name = serializers.CharField(source='english_type.name', read_only=True)
    preferred_writer_email = serializers.CharField(source='preferred_writer.email', read_only=True)
    extra_services_names = serializers.SerializerMethodField()
    can_convert = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderDraft
        fields = [
            'id',
            'website',
            'client',
            'topic',
            'order_instructions',
            'number_of_pages',
            'number_of_slides',
            'number_of_refereces',
            'deadline',
            'type_of_work',
            'type_of_work_name',
            'english_type',
            'english_type_name',
            'preferred_writer',
            'preferred_writer_email',
            'extra_services',
            'extra_services_names',
            'estimated_price',
            'title',
            'notes',
            'is_quote',
            'converted_to_order',
            'created_at',
            'updated_at',
            'last_viewed_at',
            'can_convert',
        ]
        read_only_fields = [
            'id', 'client', 'website', 'created_at', 'updated_at',
            'converted_to_order', 'estimated_price'
        ]
    
    def get_extra_services_names(self, obj):
        """Get names of extra services."""
        return [service.name for service in obj.extra_services.all()]
    
    def get_can_convert(self, obj):
        """Check if draft can be converted to order."""
        return obj.converted_to_order is None and (
            obj.topic and obj.order_instructions and obj.number_of_pages
        )
    
    def create(self, validated_data):
        """Create draft for the current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['client'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)


class OrderDraftCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order drafts."""
    
    class Meta:
        model = OrderDraft
        fields = [
            'topic',
            'order_instructions',
            'number_of_pages',
            'number_of_slides',
            'number_of_refereces',
            'deadline',
            'type_of_work',
            'english_type',
            'preferred_writer',
            'extra_services',
            'title',
            'notes',
            'is_quote',
        ]


class OrderDraftConvertSerializer(serializers.Serializer):
    """Serializer for converting draft to order."""
    calculate_price = serializers.BooleanField(default=True, help_text="Calculate price automatically")
    
    def validate(self, attrs):
        """Validate that draft can be converted."""
        draft = self.context.get('draft')
        if not draft:
            raise serializers.ValidationError("Draft not found")
        
        if draft.converted_to_order:
            raise serializers.ValidationError("Draft has already been converted")
        
        if not draft.topic or not draft.order_instructions:
            raise serializers.ValidationError("Draft is incomplete. Please fill in topic and instructions.")
        
        if not draft.number_of_pages:
            raise serializers.ValidationError("Number of pages is required")
        
        return attrs

