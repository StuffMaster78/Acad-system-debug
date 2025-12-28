"""
Website Integration Configuration Models
Stores encrypted API keys and configuration for third-party services per website.
"""
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError


class WebsiteIntegrationConfig(models.Model):
    """
    Centralized model for storing encrypted API keys and configuration
    for third-party integrations per website.
    """
    
    INTEGRATION_TYPE_CHOICES = [
        # Payment Gateways
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('razorpay', 'Razorpay'),
        ('square', 'Square'),
        ('mollie', 'Mollie'),
        
        # Email Services
        ('sendgrid', 'SendGrid'),
        ('mailgun', 'Mailgun'),
        ('ses', 'AWS SES'),
        ('postmark', 'Postmark'),
        ('sparkpost', 'SparkPost'),
        ('mandrill', 'Mandrill'),
        
        # SMS Services
        ('twilio', 'Twilio'),
        ('nexmo', 'Vonage (Nexmo)'),
        ('aws_sns', 'AWS SNS'),
        ('messagebird', 'MessageBird'),
        
        # File Storage
        ('s3', 'AWS S3'),
        ('do_spaces', 'DigitalOcean Spaces'),
        ('gcs', 'Google Cloud Storage'),
        ('azure_blob', 'Azure Blob Storage'),
        
        # CDN
        ('cloudflare', 'Cloudflare'),
        ('cloudfront', 'AWS CloudFront'),
        ('fastly', 'Fastly'),
        
        # Social Authentication
        ('google_oauth', 'Google OAuth'),
        ('facebook_oauth', 'Facebook OAuth'),
        ('github_oauth', 'GitHub OAuth'),
        ('linkedin_oauth', 'LinkedIn OAuth'),
        ('twitter_oauth', 'Twitter OAuth'),
        
        # Analytics & Tracking
        ('facebook_pixel', 'Facebook Pixel'),
        ('pinterest_tag', 'Pinterest Tag'),
        ('tiktok_pixel', 'TikTok Pixel'),
        ('hotjar', 'Hotjar'),
        ('mixpanel', 'Mixpanel'),
        ('segment', 'Segment'),
        
        # Communication
        ('intercom', 'Intercom'),
        ('zendesk', 'Zendesk'),
        ('drift', 'Drift'),
        ('crisp', 'Crisp'),
        
        # Document Processing
        ('pdf_api', 'PDF Generation API'),
        ('docu_sign', 'DocuSign'),
        ('hello_sign', 'HelloSign'),
        
        # AI Services
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('cohere', 'Cohere'),
        
        # Webhooks & Automation
        ('zapier', 'Zapier'),
        ('make', 'Make (Integromat)'),
        ('webhook', 'Custom Webhook'),
        
        # Other
        ('custom', 'Custom Integration'),
    ]
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='integration_configs',
        help_text="Website this integration belongs to"
    )
    integration_type = models.CharField(
        max_length=50,
        choices=INTEGRATION_TYPE_CHOICES,
        help_text="Type of integration"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this integration is currently active"
    )
    
    # Encrypted API keys and secrets
    encrypted_api_key = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted API key (encrypted using Fernet)"
    )
    encrypted_secret_key = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted secret key (encrypted using Fernet)"
    )
    encrypted_access_token = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted access token (encrypted using Fernet)"
    )
    
    # Public/non-sensitive configuration (stored as JSON)
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Public configuration settings (endpoints, regions, etc.)"
    )
    
    # Metadata
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom name for this integration instance"
    )
    description = models.TextField(
        blank=True,
        help_text="Description or notes about this integration"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_integrations',
        help_text="User who created this integration"
    )
    
    class Meta:
        unique_together = ['website', 'integration_type', 'name']
        indexes = [
            models.Index(fields=['website', 'integration_type']),
            models.Index(fields=['website', 'is_active']),
        ]
        verbose_name = "Website Integration Configuration"
        verbose_name_plural = "Website Integration Configurations"
    
    def __str__(self):
        name_part = f" - {self.name}" if self.name else ""
        return f"{self.website.name} - {self.get_integration_type_display()}{name_part}"
    
    def _get_cipher(self):
        """Get Fernet cipher instance for encryption/decryption."""
        encryption_key = getattr(settings, 'TOKEN_ENCRYPTION_KEY', None)
        if not encryption_key:
            raise ValidationError("TOKEN_ENCRYPTION_KEY not configured in settings")
        return Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def set_api_key(self, api_key: str):
        """Encrypt and store API key."""
        if not api_key:
            self.encrypted_api_key = None
            return
        cipher = self._get_cipher()
        self.encrypted_api_key = cipher.encrypt(api_key.encode()).decode()
    
    def get_api_key(self) -> str:
        """Decrypt and return API key."""
        if not self.encrypted_api_key:
            return ""
        cipher = self._get_cipher()
        try:
            return cipher.decrypt(self.encrypted_api_key.encode()).decode()
        except Exception as e:
            raise ValidationError(f"Failed to decrypt API key: {str(e)}")
    
    def set_secret_key(self, secret_key: str):
        """Encrypt and store secret key."""
        if not secret_key:
            self.encrypted_secret_key = None
            return
        cipher = self._get_cipher()
        self.encrypted_secret_key = cipher.encrypt(secret_key.encode()).decode()
    
    def get_secret_key(self) -> str:
        """Decrypt and return secret key."""
        if not self.encrypted_secret_key:
            return ""
        cipher = self._get_cipher()
        try:
            return cipher.decrypt(self.encrypted_secret_key.encode()).decode()
        except Exception as e:
            raise ValidationError(f"Failed to decrypt secret key: {str(e)}")
    
    def set_access_token(self, access_token: str):
        """Encrypt and store access token."""
        if not access_token:
            self.encrypted_access_token = None
            return
        cipher = self._get_cipher()
        self.encrypted_access_token = cipher.encrypt(access_token.encode()).decode()
    
    def get_access_token(self) -> str:
        """Decrypt and return access token."""
        if not self.encrypted_access_token:
            return ""
        cipher = self._get_cipher()
        try:
            return cipher.decrypt(self.encrypted_access_token.encode()).decode()
        except Exception as e:
            raise ValidationError(f"Failed to decrypt access token: {str(e)}")
    
    def save(self, *args, **kwargs):
        """Override save to ensure encryption key is available."""
        if not getattr(settings, 'TOKEN_ENCRYPTION_KEY', None):
            raise ValidationError("TOKEN_ENCRYPTION_KEY must be set in settings to use encrypted fields")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_integration(cls, website, integration_type, name=None):
        """Get active integration for a website."""
        filters = {
            'website': website,
            'integration_type': integration_type,
            'is_active': True
        }
        if name:
            filters['name'] = name
        return cls.objects.filter(**filters).first()
    
    @classmethod
    def get_integration_credentials(cls, website, integration_type, name=None):
        """Get decrypted credentials for an integration."""
        integration = cls.get_active_integration(website, integration_type, name)
        if not integration:
            return None
        
        return {
            'api_key': integration.get_api_key(),
            'secret_key': integration.get_secret_key(),
            'access_token': integration.get_access_token(),
            'config': integration.config,
        }

