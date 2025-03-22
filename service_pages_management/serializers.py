from rest_framework import serializers
from .models import (
    ServicePage, ServicePageCategory,
    ServicePageClick, ServicePageConversion
)


class ServicePageCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for service page categories.
    """
    class Meta:
        model = ServicePageCategory
        fields = '__all__'


class ServicePageSerializer(serializers.ModelSerializer):
    """
    Serializer for service pages.
    """
    class Meta:
        model = ServicePage
        read_only_fields = ['created_by', 'updated_by']
        fields = '__all__'


class ServicePageClickSerializer(serializers.ModelSerializer):
    """
    Serializer for service page clicks (read-only).
    """
    class Meta:
        model = ServicePageClick
        fields = '__all__'
        read_only_fields = fields


class ServicePageConversionSerializer(serializers.ModelSerializer):
    """
    Serializer for service page conversions (read-only).
    """
    class Meta:
        model = ServicePageConversion
        fields = '__all__'
        read_only_fields = fields