from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.core.mail import send_mail
from django.utils.text import slugify
import re  # Fix missing import
from django.utils.timezone import now  # Fix missing import
from django.contrib.postgres.fields import JSONField  # PostgreSQL JSON support
from django.conf import settings

User = settings.AUTH_USER_MODEL 

def validate_hex_color(value):
    """Ensures valid HEX color format."""
    if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", value):
        raise ValidationError("Invalid HEX color format. Example: #FFFFFF or #FFF")

class Website(models.Model):
    """
    Model to store website-specific data with enhancements for branding, SEO, and control.
    """
    # Basic website details
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Website's name"
    )
    domain = models.URLField(
        unique=True,
        help_text="Website's domain (e.g., https://example.com)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the website is currently active"
    )

    # Branding details
    logo = models.ImageField(
        upload_to='logos/',
        null=True,
        blank=True,
        help_text="Logo for the website"
    )
    theme_color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Primary theme color in HEX (e.g., #FFFFFF)"
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    ) 
    # Contact details
    contact_email = models.EmailField(
        null=True,
        blank=True,
        help_text="Support contact email for the website"
    )
    contact_phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="Support contact phone number for the website"
    )

    # SEO Metadata
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Meta title for SEO"
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="Meta description for SEO"
    )

    # Custom configurations
    allow_registration = models.BooleanField(
        default=True, help_text="Allow users to register directly on this website"
    )
    allow_guest_checkout = models.BooleanField(
        default=False,
        help_text="Allow guest checkout without account registration"
    )
    guest_requires_email_verification = models.BooleanField(
        default=True,
        help_text="Require guests to verify email before creating an order"
    )
    guest_max_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum total price allowed for guest orders. Leave blank for no explicit cap."
    )
    guest_block_urgent_before_hours = models.PositiveIntegerField(
        default=12,
        help_text="Disallow guest checkout for deadlines sooner than this many hours."
    )
    guest_magic_link_ttl_hours = models.PositiveIntegerField(
        default=72,
        help_text="Lifetime of guest magic-link access tokens in hours."
    )

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Soft delete flag"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp for soft deletion"
    )

    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Google Analytics Tracking ID (e.g., UA-123456789-1 or G-XXXXXXXXXX)"
    )
    google_search_console_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Google Search Console verification meta tag"
    )
    bing_webmaster_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Bing Webmaster Tools verification meta tag"
    )
    
    # Communication Widgets & Live Chat
    enable_live_chat = models.BooleanField(
        default=False,
        help_text="Enable live chat widget on the website"
    )
    tawkto_widget_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Tawk.to widget ID (found in Tawk.to dashboard under Administration > Property Settings)"
    )
    tawkto_property_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Tawk.to property ID (optional, for multi-property setups)"
    )
    communication_widget_type = models.CharField(
        max_length=50,
        choices=[
            ('tawkto', 'Tawk.to'),
            ('intercom', 'Intercom'),
            ('zendesk', 'Zendesk Chat'),
            ('custom', 'Custom Widget'),
        ],
        blank=True,
        null=True,
        help_text="Type of communication widget to use"
    )
    communication_widget_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration for communication widgets (JSON format)"
    )
    
    # Email Campaign Management
    default_sender_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Default sender name for emails from this website (e.g., 'ABC Support')"
    )

    default_sender_email = models.EmailField(
        null=True,
        blank=True,
        help_text="Default email address used to send emails from this website"
    )
    marketing_sender_email = models.EmailField(
        null=True, blank=True,
        help_text="Used for newsletters, promo emails (e.g., offers@site.com)"
    )

    notification_sender_email = models.EmailField(
        null=True, blank=True,
        help_text="Used for do-not-reply emails (e.g., do-not-reply@site.com)"
    )

    support_sender_email = models.EmailField(
        null=True, blank=True,
        help_text="Used for support replies (e.g., support@site.com)"
    )

    admin_notifications_email = models.EmailField(
        null=True,
        blank=True,
        help_text="Email where critical order & payment notifications are forwarded for this website (e.g., a Gmail inbox for admins).",
    )

    def validate_registration_allowed(self):
        """
        Validates if registration is allowed for this website.
        """
        if not self.allow_registration:
            raise ValidationError("Registration is disabled for this website.")

    def soft_delete(self):
        """Marks the website as deleted instead of removing it permanently."""
        self.is_deleted = True
        self.deleted_at = timezone.now()  # Use timezone-aware timestamp
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self):
        """Restores a soft-deleted website."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def clean(self):
        """Ensures domain uniqueness by ignoring 'www.'"""
        normalized_domain = self.domain.replace("www.", "")
        if Website.objects.exclude(pk=self.pk).filter(domain__iexact=normalized_domain).exists():
            raise ValidationError("A website with this domain already exists.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            counter = 2
            while Website.objects.filter(slug=base_slug).exists():
                base_slug = f"{slugify(self.name)}-{counter}"
                counter += 1
            self.slug = base_slug

        self.domain = self.domain.replace("www.", "")  # Normalize domain
        super().save(*args, **kwargs)



    class Meta:
        indexes = [
            models.Index(fields=["domain"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return self.name