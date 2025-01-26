from core.models.base import BaseModel
from django.db import models
from django.core.exceptions import ValidationError

class Website(BaseModel):
    """
    Model to store website-specific data with enhancements for branding, SEO, and control.
    """
    # Basic website details
    name = models.CharField(max_length=255, unique=True, help_text="Website's name")
    domain = models.URLField(unique=True, help_text="Website's domain (e.g., https://example.com)")
    is_active = models.BooleanField(default=True, help_text="Whether the website is currently active")

    # Branding details
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, help_text="Logo for the website")
    theme_color = models.CharField(
        max_length=7, null=True, blank=True, help_text="Primary theme color in HEX (e.g., #FFFFFF)"
    )

    # Contact details
    contact_email = models.EmailField(null=True, blank=True, help_text="Support contact email for the website")
    contact_phone = models.CharField(
        max_length=15, null=True, blank=True, help_text="Support contact phone number for the website"
    )

    # SEO Metadata
    meta_title = models.CharField(max_length=255, null=True, blank=True, help_text="Meta title for SEO")
    meta_description = models.TextField(null=True, blank=True, help_text="Meta description for SEO")

    # Custom configurations
    allow_registration = models.BooleanField(
        default=True, help_text="Allow users to register directly on this website"
    )
    allow_guest_checkout = models.BooleanField(
        default=False, help_text="Allow guest checkout without account registration"
    )

    def validate_registration_allowed(self):
        """
        Validates if registration is allowed for this website.
        """
        if not self.allow_registration:
            raise ValidationError("Registration is disabled for this website.")

    def __str__(self):
        return self.name