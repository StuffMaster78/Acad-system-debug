from rest_framework import serializers
from .models import (
    PricingConfiguration,
    AdditionalService,
    AcademicLevelPricing,
    WriterLevelOptionConfig,
    TypeOfWorkMultiplier,
    DeadlineMultiplier,
    PreferredWriterConfig
)


class PricingConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for the PricingConfiguration model."""

    class Meta:
        model = PricingConfiguration
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']


class AdditionalServiceSerializer(serializers.ModelSerializer):
    """Serializer for the AdditionalService model."""

    class Meta:
        model = AdditionalService
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']


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

    class Meta:
        model = DeadlineMultiplier
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']


class PreferredWriterConfigSerializer(serializers.ModelSerializer):
    """Serializer for the PreferredWriterConfig model."""

    class Meta:
        model = PreferredWriterConfig
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']


class WriterLevelOptionConfigSerializer(serializers.ModelSerializer):
    """Serializer for the WriterLevelOptionConfig model."""

    class Meta:
        model = WriterLevelOptionConfig
        fields = '__all__'
        read_only_fields = ['website', 'created_at', 'updated_at']

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