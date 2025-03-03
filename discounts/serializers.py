from rest_framework import serializers
from .models import Discount, SeasonalEvent
from django.utils.timezone import now

class SeasonalEventSerializer(serializers.ModelSerializer):
    """Serializer for Seasonal Events."""
    
    class Meta:
        model = SeasonalEvent
        fields = ["id", "name", "description", "start_date", "end_date", "is_active"]
        read_only_fields = ["is_active"]  # Prevent updating is_active directly

class DiscountSerializer(serializers.ModelSerializer):
    """Serializer for Discounts."""
    
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = [
            "id", "code", "description", "discount_type", "value",
            "max_uses", "used_count", "start_date", "end_date", "min_order_value",
            "is_general", "assigned_to_client", "seasonal_event", "is_active", "is_valid"
        ]
        read_only_fields = ["used_count", "is_valid"]

    def get_is_valid(self, obj):
        """Returns whether the discount is currently valid."""
        return obj.is_valid()

    def validate(self, data):
        """Custom validation for discounts."""
        if data["discount_type"] == "percentage" and (data["value"] <= 0 or data["value"] > 100):
            raise serializers.ValidationError("Percentage discount must be between 1 and 100.")
        if "start_date" in data and "end_date" in data and data["start_date"] > data["end_date"]:
            raise serializers.ValidationError("End date must be after the start date.")
        if "max_uses" in data and data["max_uses"] is not None and data["max_uses"] <= 0:
            raise serializers.ValidationError("Max uses must be a positive number.")
        return data

    def create(self, validated_data):
        """Ensure discount code uniqueness if not provided."""
        if not validated_data.get("code"):
            validated_data["code"] = Discount.generate_unique_code()
        return super().create(validated_data)
