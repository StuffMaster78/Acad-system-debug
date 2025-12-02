"""
Tenant Features Serializers
"""
from rest_framework import serializers
from websites.models.tenant_features import TenantBranding, TenantFeatureToggle


class TenantBrandingSerializer(serializers.ModelSerializer):
    """Serializer for tenant branding."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = TenantBranding
        fields = [
            'id', 'website', 'website_name',
            'email_subject_prefix', 'email_reply_to',
            'email_from_name', 'email_from_address',
            'notification_subject_prefix',
            'email_logo_url', 'email_header_color', 'email_footer_text',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantBrandingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tenant branding."""
    
    class Meta:
        model = TenantBranding
        fields = [
            'email_subject_prefix', 'email_reply_to',
            'email_from_name', 'email_from_address',
            'notification_subject_prefix',
            'email_logo_url', 'email_header_color', 'email_footer_text'
        ]


class TenantFeatureToggleSerializer(serializers.ModelSerializer):
    """Serializer for tenant feature toggles."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = TenantFeatureToggle
        fields = [
            'id', 'website', 'website_name',
            'magic_link_enabled', 'two_factor_required', 'password_reset_enabled',
            'messaging_enabled', 'messaging_types_allowed',
            'max_order_size_pages', 'max_order_size_slides',
            'allow_order_drafts', 'allow_order_presets',
            'allow_writer_portfolios', 'allow_writer_feedback',
            'allow_wallet', 'allow_advance_payments',
            'allow_class_orders', 'allow_disputes', 'allow_escalations',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantFeatureToggleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tenant feature toggles."""
    
    class Meta:
        model = TenantFeatureToggle
        fields = [
            'magic_link_enabled', 'two_factor_required', 'password_reset_enabled',
            'messaging_enabled', 'messaging_types_allowed',
            'max_order_size_pages', 'max_order_size_slides',
            'allow_order_drafts', 'allow_order_presets',
            'allow_writer_portfolios', 'allow_writer_feedback',
            'allow_wallet', 'allow_advance_payments',
            'allow_class_orders', 'allow_disputes', 'allow_escalations'
        ]

