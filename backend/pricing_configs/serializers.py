from rest_framework import serializers
from websites.models import Website
from .models import (
    PricingConfiguration,
    AdditionalService,
    AcademicLevelPricing,
    WriterLevelOptionConfig,
    TypeOfWorkMultiplier,
    DeadlineMultiplier,
    PreferredWriterConfig,
)
from pricing.models.calculator_session import PricingCalculatorSession


class PricingConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for the PricingConfiguration model."""
    website = serializers.SerializerMethodField()
    
    class Meta:
        model = PricingConfiguration
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None


class AdditionalServiceSerializer(serializers.ModelSerializer):
    """Serializer for the AdditionalService model."""
    website = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all(), required=False, allow_null=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        model = AdditionalService
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at', 'website_name', 'website_domain']


class AcademicLevelPricingSerializer(serializers.ModelSerializer):
    """Serializer for the AcademicLevelPricing model."""

    class Meta:
        model = AcademicLevelPricing
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']


class TypeOfWorkMultiplierSerializer(serializers.ModelSerializer):
    """Serializer for the TypeOfWorkMultiplier model."""

    class Meta:
        model = TypeOfWorkMultiplier
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']


class DeadlineMultiplierSerializer(serializers.ModelSerializer):
    """Serializer for the DeadlineMultiplier model."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        model = DeadlineMultiplier
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'website_name', 'website_domain']


class PreferredWriterConfigSerializer(serializers.ModelSerializer):
    """Serializer for the PreferredWriterConfig model."""
    website = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all(), required=False, allow_null=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        model = PreferredWriterConfig
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at', 'website_name', 'website_domain']


class WriterLevelOptionConfigSerializer(serializers.ModelSerializer):
    """Serializer for the WriterLevelOptionConfig model."""
    website = serializers.PrimaryKeyRelatedField(queryset=Website.objects.all(), required=False, allow_null=True)
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)

    class Meta:
        model = WriterLevelOptionConfig
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at', 'website_name', 'website_domain']


class PriceEstimationInputSerializer(serializers.Serializer):
    """Serializer for input data required to estimate the price of an order."""
    website = serializers.PrimaryKeyRelatedField(read_only=True)

    num_pages = serializers.IntegerField(min_value=0, required=False, default=0)
    num_slides = serializers.IntegerField(min_value=0, required=False, default=0)

    academic_level = serializers.IntegerField(required=True)
    deadline_hours = serializers.IntegerField(required=True)
    order_type = serializers.CharField(required=False, allow_blank=True)
    is_technical = serializers.BooleanField(default=False)

    preferred_writer = serializers.CharField(required=False, allow_blank=True)
    writer_tier = serializers.CharField(required=False, allow_blank=True)
    writer_quality = serializers.CharField(required=False, allow_blank=True)

    additional_services = serializers.ListField(
        child=serializers.SlugField(), required=False, default=[]
    )


class PricingCalculatorSessionSerializer(serializers.ModelSerializer):
    """Serializer for Pricing Calculator Session"""
    
    class Meta:
        model = PricingCalculatorSession
        fields = [
            'id',
            'session_key',
            'user',
            'order_data',
            'calculated_price',
            'base_price',
            'adjustments',
            'discount_code',
            'discount_amount',
            'final_price',
            'created_at',
            'expires_at',
            'converted_to_order',
            'order_id',
            'is_expired',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'expires_at',
            'converted_to_order',
            'order_id',
            'is_expired',
        ]
