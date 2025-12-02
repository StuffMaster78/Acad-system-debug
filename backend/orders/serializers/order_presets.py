"""
Order Presets Serializers
"""
from rest_framework import serializers
from orders.order_presets import OrderPreset


class OrderPresetSerializer(serializers.ModelSerializer):
    """Serializer for order presets."""
    default_type_of_work_name = serializers.CharField(source='default_type_of_work.name', read_only=True)
    default_english_type_name = serializers.CharField(source='default_english_type.name', read_only=True)
    preferred_writer_email = serializers.CharField(source='preferred_writer.email', read_only=True)
    default_extra_services_names = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderPreset
        fields = [
            'id',
            'website',
            'client',
            'name',
            'description',
            'default_type_of_work',
            'default_type_of_work_name',
            'default_english_type',
            'default_english_type_name',
            'default_spacing',
            'default_number_of_refereces',
            'preferred_writer',
            'preferred_writer_email',
            'default_extra_services',
            'default_extra_services_names',
            'style_preferences',
            'usage_count',
            'last_used_at',
            'is_active',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'client', 'website', 'usage_count', 'last_used_at',
            'created_at', 'updated_at'
        ]
    
    def get_default_extra_services_names(self, obj):
        """Get names of default extra services."""
        return [service.name for service in obj.default_extra_services.all()]
    
    def create(self, validated_data):
        """Create preset for the current user."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['client'] = request.user
            validated_data['website'] = request.user.website
            
            # If this is set as default, unset other defaults
            if validated_data.get('is_default', False):
                OrderPreset.objects.filter(
                    client=request.user,
                    website=request.user.website,
                    is_default=True
                ).update(is_default=False)
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update preset."""
        # If setting as default, unset other defaults
        if validated_data.get('is_default', False) and not instance.is_default:
            OrderPreset.objects.filter(
                client=instance.client,
                website=instance.website,
                is_default=True
            ).exclude(id=instance.id).update(is_default=False)
        
        return super().update(instance, validated_data)


class OrderPresetApplySerializer(serializers.Serializer):
    """Serializer for applying preset to draft or order."""
    target_type = serializers.ChoiceField(
        choices=['draft', 'order'],
        help_text="Whether to apply to a draft or order"
    )
    target_id = serializers.IntegerField(
        required=False,
        help_text="ID of draft or order to apply to (if not provided, creates new)"
    )

