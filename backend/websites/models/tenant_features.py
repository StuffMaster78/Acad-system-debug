"""
Multi-Tenant Features Model
Per-tenant branding and feature toggles.
"""
from django.db import models
# Use string reference to avoid circular import
# Website will be resolved by Django's model loading


class TenantBranding(models.Model):
    """
    Per-tenant branding for emails and notifications.
    """
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='branding'
    )
    
    # Email branding
    email_subject_prefix = models.CharField(
        max_length=50,
        blank=True,
        help_text="Prefix for email subjects (e.g., '[YourSite]')"
    )
    email_reply_to = models.EmailField(
        blank=True,
        help_text="Reply-to address for emails"
    )
    email_from_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="From name for emails (e.g., 'YourSite Support')"
    )
    email_from_address = models.EmailField(
        blank=True,
        help_text="From address for emails"
    )
    
    # Notification branding
    notification_subject_prefix = models.CharField(
        max_length=50,
        blank=True,
        help_text="Prefix for notification subjects"
    )
    
    # Logo and colors
    email_logo_url = models.URLField(
        blank=True,
        help_text="Logo URL for email templates"
    )
    email_header_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Header color for emails (HEX)"
    )
    email_footer_text = models.TextField(
        blank=True,
        help_text="Footer text for emails"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tenant Branding"
        verbose_name_plural = "Tenant Branding"
    
    def __str__(self):
        return f"Branding for {self.website.name}"


class TenantFeatureToggle(models.Model):
    """
    Tenant-specific feature toggles.
    """
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='feature_toggles'
    )
    
    # Authentication features
    magic_link_enabled = models.BooleanField(
        default=True,
        help_text="Allow magic link authentication"
    )
    two_factor_required = models.BooleanField(
        default=False,
        help_text="Require 2FA for all users"
    )
    password_reset_enabled = models.BooleanField(
        default=True,
        help_text="Allow password reset"
    )
    
    # Messaging features
    messaging_enabled = models.BooleanField(
        default=True,
        help_text="Enable messaging system"
    )
    messaging_types_allowed = models.JSONField(
        default=list,
        blank=True,
        help_text="Allowed messaging types: ['order_messages', 'direct_messages', 'group_messages']"
    )
    
    # Order features
    max_order_size_pages = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum pages per order (null = unlimited)"
    )
    max_order_size_slides = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum slides per order (null = unlimited)"
    )
    allow_order_drafts = models.BooleanField(
        default=True,
        help_text="Allow saving order drafts"
    )
    allow_order_presets = models.BooleanField(
        default=True,
        help_text="Allow order presets"
    )
    
    # Writer features
    allow_writer_portfolios = models.BooleanField(
        default=True,
        help_text="Allow writer portfolios"
    )
    allow_writer_feedback = models.BooleanField(
        default=True,
        help_text="Allow feedback system"
    )
    
    # Payment features
    allow_wallet = models.BooleanField(
        default=True,
        help_text="Allow wallet payments"
    )
    allow_advance_payments = models.BooleanField(
        default=True,
        help_text="Allow advance payments for writers"
    )
    
    # Advanced features
    allow_class_orders = models.BooleanField(
        default=True,
        help_text="Allow class/bulk orders"
    )
    allow_disputes = models.BooleanField(
        default=True,
        help_text="Allow order disputes"
    )
    allow_escalations = models.BooleanField(
        default=True,
        help_text="Allow escalation flows"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tenant Feature Toggle"
        verbose_name_plural = "Tenant Feature Toggles"
    
    def __str__(self):
        return f"Feature toggles for {self.website.name}"
    
    def is_feature_enabled(self, feature_name):
        """Check if a feature is enabled."""
        feature_map = {
            'magic_link': self.magic_link_enabled,
            '2fa_required': self.two_factor_required,
            'messaging': self.messaging_enabled,
            'order_drafts': self.allow_order_drafts,
            'order_presets': self.allow_order_presets,
            'writer_portfolios': self.allow_writer_portfolios,
            'writer_feedback': self.allow_writer_feedback,
            'wallet': self.allow_wallet,
            'advance_payments': self.allow_advance_payments,
            'class_orders': self.allow_class_orders,
            'disputes': self.allow_disputes,
            'escalations': self.allow_escalations,
        }
        return feature_map.get(feature_name, False)

