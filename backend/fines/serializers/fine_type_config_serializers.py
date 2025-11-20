"""
Serializers for FineTypeConfig model.
"""

from rest_framework import serializers
from fines.models.fine_type_config import FineTypeConfig


class FineTypeConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for FineTypeConfig - admin-configurable fine types.
    """
    website_domain = serializers.CharField(source='website.domain', read_only=True, allow_null=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = FineTypeConfig
        fields = [
            'id', 'code', 'name', 'description',
            'is_system_defined', 'calculation_type',
            'fixed_amount', 'percentage', 'base_amount',
            'min_amount', 'max_amount',
            'website', 'website_domain',
            'active', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def validate(self, data):
        """Validate fine type configuration."""
        calculation_type = data.get('calculation_type', self.instance.calculation_type if self.instance else 'fixed')
        
        if calculation_type == 'fixed':
            if not data.get('fixed_amount') and not (self.instance and self.instance.fixed_amount):
                raise serializers.ValidationError({
                    'fixed_amount': 'Fixed amount is required for fixed calculation type.'
                })
        
        elif calculation_type == 'percentage':
            if not data.get('percentage') and not (self.instance and self.instance.percentage):
                raise serializers.ValidationError({
                    'percentage': 'Percentage is required for percentage calculation type.'
                })
        
        elif calculation_type == 'progressive_hourly':
            code = data.get('code', self.instance.code if self.instance else None)
            if code != 'late_submission':
                raise serializers.ValidationError({
                    'calculation_type': 'Progressive hourly only available for late_submission fine type.'
                })
        
        # Validate min/max
        min_amount = data.get('min_amount')
        max_amount = data.get('max_amount')
        if min_amount and max_amount and min_amount > max_amount:
            raise serializers.ValidationError({
                'min_amount': 'Min amount cannot be greater than max amount.'
            })
        
        return data
    
    def validate_code(self, value):
        """Validate code is unique per website."""
        queryset = FineTypeConfig.objects.filter(code=value)
        
        # If updating, exclude current instance
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        # Check if code exists for this website or global
        website = self.initial_data.get('website') or (self.instance.website if self.instance else None)
        if website:
            if queryset.filter(website=website).exists():
                raise serializers.ValidationError(
                    f"Fine type with code '{value}' already exists for this website."
                )
        else:
            # Global fine type - ensure no website-specific conflicts
            if queryset.filter(website__isnull=True).exists():
                raise serializers.ValidationError(
                    f"Global fine type with code '{value}' already exists."
                )
        
        return value

