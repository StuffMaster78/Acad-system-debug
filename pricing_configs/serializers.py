from rest_framework import serializers
from .models import PricingConfiguration, AdditionalService


class PricingConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for the PricingConfiguration model.
    """

    class Meta:
        model = PricingConfiguration
        fields = '__all__'  # Include all fields
        read_only_fields = ['website']  # Website should be set automatically


class AdditionalServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the AdditionalService model.
    """

    class Meta:
        model = AdditionalService
        fields = '__all__'  # Include all fields
        read_only_fields = ['website']  # Website should be set automatically