"""
Serializers for LatenessFineRule model.
"""

from rest_framework import serializers
from fines.models.late_fine_policy import LatenessFineRule


class LatenessFineRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for LatenessFineRule - admin configurable fine rules.
    """
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_active_now = serializers.SerializerMethodField()
    
    class Meta:
        model = LatenessFineRule
        fields = [
            'id', 'website', 'website_domain',
            'first_hour_percentage', 'second_hour_percentage', 'third_hour_percentage',
            'subsequent_hours_percentage', 'daily_rate_percentage',
            'max_fine_percentage', 'calculation_mode', 'base_amount',
            'active', 'start_date', 'end_date', 'description',
            'created_by', 'created_by_username', 'created_at', 'updated_at',
            'is_active_now'
        ]
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_is_active_now(self, obj):
        """Check if rule is currently active."""
        return obj.is_active()
    
    def validate(self, data):
        """Validate that percentages are reasonable."""
        if data.get('first_hour_percentage', 0) < 0:
            raise serializers.ValidationError("First hour percentage cannot be negative.")
        if data.get('max_fine_percentage') and data['max_fine_percentage'] > 100:
            raise serializers.ValidationError("Max fine percentage cannot exceed 100%.")
        return data

