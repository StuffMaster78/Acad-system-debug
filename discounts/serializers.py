from rest_framework import serializers
from .models import Discount, DiscountUsage
from websites.models import Website
from users.models import User
from models.seasonal_event import SeasonalEvent
from models.stacking import DiscountStackingRule
from django.utils.timezone import now
from decimal import Decimal

class DiscountSerializer(serializers.ModelSerializer):
    """
    Serializer for Discount model
    """
    website = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all())
    assigned_to_client = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    seasonal_event = serializers.PrimaryKeyRelatedField(queryset=SeasonalEvent.objects.all(), required=False)
    
    class Meta:
        model = Discount
        fields = [
            'id', 'website', 'code', 'description', 'discount_type', 
            'origin_type', 'value', 'max_uses', 'used_count', 
            'start_date', 'end_date', 'min_order_value', 
            'max_discount_value', 'applies_to_first_order_only', 
            'is_general', 'assigned_to_client', 'seasonal_event', 
            'stackable', 'stackable_with', 'max_discount_percent', 
            'max_stackable_uses_per_customer', 'is_active', 'is_deleted'
        ]
        read_only_fields = ['used_count', 'is_deleted']

    def validate_code(self, value):
        """
        Ensure discount code is unique per website
        """
        if Discount.objects.filter(code=value, website=self.context['website'], is_deleted=False).exists():
            raise serializers.ValidationError("Discount code must be unique per website.")
        return value

    def create(self, validated_data):
        """
        Custom create logic to handle code generation or other logic
        """
        discount = Discount.objects.create(**validated_data)
        return discount
    
    def update(self, instance, validated_data):
        """
        Handle updates of the discount
        """
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

class DiscountUsageSerializer(serializers.ModelSerializer):
    """
    Serializer for DiscountUsage model
    """
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    base_discount = DiscountSerializer()
    stackable_with = DiscountSerializer()

    class Meta:
        model = DiscountUsage
        fields = ['id', 'website', 'user', 'base_discount', 'stackable_with', 'used_at']
        read_only_fields = ['used_at']

    def validate(self, data):
        """
        Check if stackable discounts are valid or if any business rules are violated
        """
        base_discount = data.get('base_discount')
        stackable_with = data.get('stackable_with')
        
        if base_discount and stackable_with:
            if base_discount.id == stackable_with.id:
                raise serializers.ValidationError("A discount cannot stack with itself.")
            # Add additional logic here to enforce discount stacking rules
        
        return data


class SeasonalEventSerializer(serializers.ModelSerializer):
    """
    Serializer for SeasonalEvent model
    """
    class Meta:
        model = SeasonalEvent
        fields = [
            'id', 'name', 'start_date', 'end_date', 
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_start_date(self, value):
        """
        Ensure the start date is not in the past.
        """
        if value < now():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value

    def validate_end_date(self, value):
        """
        Ensure the end date is after the start date.
        """
        start_date = self.initial_data.get('start_date')
        if start_date and value < start_date:
            raise serializers.ValidationError("End date cannot be before start date.")
        return value

    def create(self, validated_data):
        """
        Custom create method to handle creation of seasonal event.
        """
        event = SeasonalEvent.objects.create(**validated_data)
        return event

    def update(self, instance, validated_data):
        """
        Handle update of a seasonal event.
        """
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
    
class SeasonalEventWithDiscountsSerializer(SeasonalEventSerializer):
    """
    Serializer for SeasonalEvent that includes discounts attached to the event.
    """
    discounts = serializers.PrimaryKeyRelatedField(
        queryset=Discount.objects.all(), 
        many=True,
        required=False
    )

    class Meta:
        model = SeasonalEvent
        fields = SeasonalEventSerializer.Meta.fields + ['discounts']
    
    def validate(self, data):
        """
        Custom validation for the event and discounts.
        """
        discounts = data.get('discounts', [])
        if discounts:
            # Example validation: Ensure discounts are valid for this event
            for discount in discounts:
                if not discount.is_active:
                    raise serializers.ValidationError(f"Discount {discount.code} is not active.")
        return data
    

class DiscountStackingRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for DiscountStackingRule model.

    Converts DiscountStackingRule instances to JSON format and validates
    data before saving or updating.
    """
    base_discount = serializers.PrimaryKeyRelatedField(queryset=Discount.objects.all())
    stackable_discount = serializers.PrimaryKeyRelatedField(queryset=Discount.objects.all())

    class Meta:
        model = DiscountStackingRule
        fields = ['id', 'base_discount', 'stackable_discount']

    def validate(self, data):
        """
        Ensure that base discount and stackable discount are not the same.

        Validates that both discounts involved in the stacking rule are distinct
        and the stacking rule is valid based on business logic.
        """
        base_discount = data.get("base_discount")
        stackable_discount = data.get("stackable_discount")

        if base_discount == stackable_discount:
            raise serializers.ValidationError("Base discount and stackable discount cannot be the same.")

        if not stackable_discount.stackable:
            raise serializers.ValidationError(
                f"{stackable_discount.code} cannot be stacked with other discounts."
            )

        return data

    def create(self, validated_data):
        """
        Create a new DiscountStackingRule instance.

        Calls the parent class's create method after validating the data.
        """
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing DiscountStackingRule instance.

        Calls the parent class's update method after validating the data.
        """
        return super().update(instance, validated_data)