"""
Serializers for SEO Pages.
"""
from rest_framework import serializers
from .models import SeoPage


class SeoPageSerializer(serializers.ModelSerializer):
    """Serializer for SEO Page (admin/internal use)."""
    
    class Meta:
        model = SeoPage
        fields = [
            'id', 'website', 'title', 'slug', 'meta_title', 'meta_description',
            'blocks', 'is_published', 'publish_date', 'created_by', 'updated_by',
            'created_at', 'updated_at', 'is_deleted', 'deleted_at'
        ]
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']


class PublicSeoPageSerializer(serializers.ModelSerializer):
    """Public serializer for SEO Page (read-only, excludes internal fields)."""
    
    class Meta:
        model = SeoPage
        fields = [
            'id', 'title', 'slug', 'meta_title', 'meta_description',
            'blocks', 'publish_date'
        ]
        read_only_fields = fields

