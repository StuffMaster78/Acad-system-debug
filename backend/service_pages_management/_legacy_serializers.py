from rest_framework import serializers
from datetime import timedelta
from django.utils.timezone import now
from websites.models import Website
from .models import (
    ServicePage,
    ServicePageClick,
    ServicePageConversion
)
try:
    from .models.enhanced_models import ServicePageFAQ, ServicePageResource
except ImportError:
    ServicePageFAQ = None
    ServicePageResource = None


class FAQItemSerializer(serializers.Serializer):
    """
    Validates each item in the faq_json list.
    """
    question = serializers.CharField()
    answer = serializers.CharField()


class ServicePageFAQWriteSerializer(serializers.Serializer):
    """Serializer for writing FAQs."""
    question = serializers.CharField(max_length=500)
    answer = serializers.CharField()


class ServicePageResourceWriteSerializer(serializers.Serializer):
    """Serializer for writing Resources."""
    title = serializers.CharField(max_length=255)
    url = serializers.URLField()
    description = serializers.CharField(required=False, allow_blank=True)
    resource_type = serializers.CharField(max_length=50, required=False, default='link')


class ServicePageSerializer(serializers.ModelSerializer):
    """
    Serializer for managing service pages with SEO and FAQ data.
    """
    faq_json = FAQItemSerializer(many=True, required=False)
    faqs_data = ServicePageFAQWriteSerializer(many=True, write_only=True, required=False)
    resources_data = ServicePageResourceWriteSerializer(many=True, write_only=True, required=False)
    website_id = serializers.PrimaryKeyRelatedField(
        queryset=Website.objects.filter(is_active=True, is_deleted=False),  # Default queryset, can be overridden in __init__
        source='website',
        write_only=True,
        required=False,
        allow_null=False
    )
    website = serializers.SerializerMethodField()

    class Meta:
        model = ServicePage
        fields = [
            'id',
            'website',
            'website_id',
            'title',
            'slug',
            'header',
            'content',
            'meta_title',
            'meta_description',
            'image',
            'og_image',
            'faq_json',
            'faqs_data',
            'resources_data',
            'is_published',
            'publish_date',
            'is_deleted',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
            'website'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for website_id based on request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.role == 'superadmin':
                from websites.models import Website
                self.fields['website_id'].queryset = Website.objects.filter(is_active=True, is_deleted=False)
            else:
                user_website = getattr(user, 'website', None)
                if user_website:
                    from websites.models import Website
                    self.fields['website_id'].queryset = Website.objects.filter(id=user_website.id, is_active=True, is_deleted=False)
                else:
                    from websites.models import Website
                    self.fields['website_id'].queryset = Website.objects.none()
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None

    def validate_faq_json(self, value):
        """
        Ensures faq_json is a list of dictionaries with Q&A.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("FAQ must be a list.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    "Each FAQ item must be a dictionary."
                )
            if 'question' not in item or 'answer' not in item:
                raise serializers.ValidationError(
                    "Each FAQ must include 'question' and 'answer'."
                )
        return value
    
    def create(self, validated_data):
        """Create service page with FAQs and resources."""
        faqs_data = validated_data.pop('faqs_data', [])
        resources_data = validated_data.pop('resources_data', [])
        
        service_page = super().create(validated_data)
        
        # Create FAQs if ServicePageFAQ model exists
        if ServicePageFAQ and faqs_data:
            for faq_data in faqs_data:
                ServicePageFAQ.objects.create(
                    service_page=service_page,
                    question=faq_data.get('question'),
                    answer=faq_data.get('answer')
                )
        
        # Create Resources if ServicePageResource model exists
        if ServicePageResource and resources_data:
            for resource_data in resources_data:
                ServicePageResource.objects.create(
                    service_page=service_page,
                    title=resource_data.get('title'),
                    url=resource_data.get('url'),
                    description=resource_data.get('description', ''),
                    resource_type=resource_data.get('resource_type', 'link')
                )
        
        return service_page
    
    def update(self, instance, validated_data):
        """Update service page with FAQs and resources."""
        faqs_data = validated_data.pop('faqs_data', None)
        resources_data = validated_data.pop('resources_data', None)
        
        service_page = super().update(instance, validated_data)
        
        # Update FAQs if provided and ServicePageFAQ model exists
        if ServicePageFAQ and faqs_data is not None:
            # Delete existing FAQs
            ServicePageFAQ.objects.filter(service_page=service_page).delete()
            # Create new FAQs
            for faq_data in faqs_data:
                ServicePageFAQ.objects.create(
                    service_page=service_page,
                    question=faq_data.get('question'),
                    answer=faq_data.get('answer')
                )
        
        # Update Resources if provided and ServicePageResource model exists
        if ServicePageResource and resources_data is not None:
            # Delete existing resources
            ServicePageResource.objects.filter(service_page=service_page).delete()
            # Create new resources
            for resource_data in resources_data:
                ServicePageResource.objects.create(
                    service_page=service_page,
                    title=resource_data.get('title'),
                    url=resource_data.get('url'),
                    description=resource_data.get('description', ''),
                    resource_type=resource_data.get('resource_type', 'link')
                )
        
        return service_page


class ServicePageAnalyticsSerializer(serializers.ModelSerializer):
    """
    Read-only analytics data for a service page.
    Supports ?days=N filtering via serializer context.
    """
    click_count = serializers.SerializerMethodField()
    conversion_count = serializers.SerializerMethodField()
    since = serializers.SerializerMethodField()

    class Meta:
        model = ServicePage
        fields = [
            'id',
            'title',
            'slug',
            'is_published',
            'publish_date',
            'click_count',
            'conversion_count',
            'since'
        ]

    def get_days(self):
        try:
            return int(self.context.get('days', 30))
        except (ValueError, TypeError):
            return 30

    def get_since(self, obj):
        return (now() - timedelta(days=self.get_days())).isoformat()

    def get_click_count(self, obj):
        since = now() - timedelta(days=self.get_days())
        return ServicePageClick.objects.filter(
            service_page=obj,
            timestamp__gte=since
        ).count()

    def get_conversion_count(self, obj):
        since = now() - timedelta(days=self.get_days())
        return ServicePageConversion.objects.filter(
            service_page=obj,
            timestamp__gte=since
        ).count()