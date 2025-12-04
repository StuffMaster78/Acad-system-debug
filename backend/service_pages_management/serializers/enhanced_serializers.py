"""
Enhanced serializers for service pages - SEO, FAQs, Resources, CTAs.
"""
from rest_framework import serializers
from ..models import ServicePage, ServicePageClick, ServicePageConversion
from ..models.enhanced_models import (
    ServicePageFAQ, ServicePageResource, ServicePageCTA,
    ServicePageSEOMetadata, ServicePageEditHistory, ServicePageContentBlock
)
from ..models.pdf_samples import ServicePagePDFSampleSection
from ..serializers.pdf_serializers import ServicePagePDFSampleSectionSerializer


class ServicePageFAQSerializer(serializers.ModelSerializer):
    """Serializer for service page FAQs."""
    
    class Meta:
        model = ServicePageFAQ
        fields = [
            'id', 'service_page', 'question', 'answer', 'question_slug',
            'display_order', 'is_featured', 'upvote_count', 'accepted_answer'
        ]
        read_only_fields = ['question_slug']


class ServicePageResourceSerializer(serializers.ModelSerializer):
    """Serializer for service page resources."""
    
    class Meta:
        model = ServicePageResource
        fields = [
            'id', 'service_page', 'title', 'url', 'description',
            'resource_type', 'display_order'
        ]


class ServicePageCTASerializer(serializers.ModelSerializer):
    """Serializer for service page CTAs."""
    
    class Meta:
        model = ServicePageCTA
        fields = [
            'id', 'service_page', 'title', 'description', 'button_text',
            'button_url', 'style', 'display_order', 'is_active'
        ]


class ServicePageSEOMetadataSerializer(serializers.ModelSerializer):
    """Serializer for service page SEO metadata."""
    
    class Meta:
        model = ServicePageSEOMetadata
        fields = [
            'id', 'service_page', 'keywords', 'article_type',
            'og_type', 'og_title', 'og_description', 'og_image',
            'og_url', 'og_site_name', 'twitter_card_type',
            'twitter_title', 'twitter_description', 'twitter_image',
            'twitter_site', 'schema_breadcrumb', 'schema_organization',
            'schema_rating', 'google_business_url', 'canonical_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ServicePageEditHistorySerializer(serializers.ModelSerializer):
    """Serializer for service page edit history."""
    edited_by_username = serializers.CharField(source='edited_by.username', read_only=True)
    
    class Meta:
        model = ServicePageEditHistory
        fields = [
            'id', 'service_page', 'edited_by', 'edited_by_username',
            'previous_content', 'current_content', 'changes_summary',
            'fields_changed', 'edited_at'
        ]
        read_only_fields = ['edited_at']


class EnhancedServicePageSerializer(serializers.ModelSerializer):
    """Enhanced service page serializer with all new features."""
    faqs = ServicePageFAQSerializer(many=True, read_only=True)
    resources = ServicePageResourceSerializer(many=True, read_only=True)
    ctas = ServicePageCTASerializer(many=True, read_only=True)
    pdf_sample_sections = ServicePagePDFSampleSectionSerializer(many=True, read_only=True)
    seo_metadata = ServicePageSEOMetadataSerializer(read_only=True)
    edit_history_count = serializers.SerializerMethodField()
    
    # Schema.org JSON
    schema_json = serializers.SerializerMethodField()
    og_tags = serializers.SerializerMethodField()
    twitter_tags = serializers.SerializerMethodField()
    
    # Analytics
    click_count = serializers.SerializerMethodField()
    conversion_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicePage
        fields = [
            'id', 'website', 'title', 'slug', 'header', 'content', 'image',
            'meta_title', 'meta_description', 'og_image', 'is_published',
            'publish_date', 'created_by', 'updated_by', 'created_at',
            'updated_at', 'is_deleted', 'faqs', 'resources', 'ctas',
            'pdf_sample_sections', 'seo_metadata', 'edit_history_count',
            'schema_json', 'og_tags', 'twitter_tags', 'click_count', 'conversion_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_edit_history_count(self, obj):
        """Get count of edit history entries."""
        try:
            return ServicePageEditHistory.objects.filter(service_page=obj).count()
        except Exception:
            return 0
    
    def get_schema_json(self, obj):
        """Get Schema.org structured data."""
        try:
            from ..services.seo_service import ServicePageSEOService
            return ServicePageSEOService.get_all_schemas_for_service_page(obj)
        except Exception:
            return {}
    
    def get_og_tags(self, obj):
        """Get Open Graph meta tags."""
        try:
            from ..services.seo_service import ServicePageSEOService
            return ServicePageSEOService.get_open_graph_tags(obj)
        except Exception:
            return {}
    
    def get_twitter_tags(self, obj):
        """Get Twitter Card meta tags."""
        try:
            from ..services.seo_service import ServicePageSEOService
            return ServicePageSEOService.get_twitter_card_tags(obj)
        except Exception:
            return {}
    
    def get_click_count(self, obj):
        """Get total click count for this service page."""
        try:
            return ServicePageClick.objects.filter(service_page=obj).count()
        except Exception:
            return 0
    
    def get_conversion_count(self, obj):
        """Get total conversion count for this service page."""
        try:
            return ServicePageConversion.objects.filter(service_page=obj).count()
        except Exception:
            return 0


class ServicePageContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for content blocks in service pages."""
    template = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicePageContentBlock
        fields = [
            'id', 'service_page', 'template', 'position',
            'auto_insert', 'custom_data', 'is_active', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_template(self, obj):
        """Get template details."""
        from blog_pages_management.serializers.enhanced_serializers import ContentBlockTemplateSerializer
        return ContentBlockTemplateSerializer(obj.template).data

