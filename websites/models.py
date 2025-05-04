# from core.models.base import BaseModel
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone 
from django.core.mail import send_mail
from django.utils.text import slugify
import re  # Fix missing import
from django.utils.timezone import now  # Fix missing import
from django.contrib.postgres.fields import JSONField  # PostgreSQL JSON support
from django.conf import settings

User = get_user_model()

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
        help_text="Google Analytics Tracking ID (e.g., UA-XXXXX-X or G-XXXXXXXXXX)"
    )
    google_search_console_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Google Search Console verification meta tag"
    )
    bing_webmaster_id = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Bing Webmaster Tools verification meta tag"
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


class WebsiteActionLog(models.Model):
    """Logs admin actions for website updates (SEO settings, deletions, etc.)."""
    ACTION_CHOICES = [
        ("SEO_UPDATED", "SEO Settings Updated"),
        ("SOFT_DELETED", "Website Soft Deleted"),
        ("RESTORED", "Website Restored"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="action_logs"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    details = models.TextField(
        blank=True,
        null=True,
        help_text="Extra details about the action"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} on {self.website.name} at {self.timestamp}"


class WebsiteStaticPage(models.Model):
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="static_pages"
    )
    title = models.CharField(max_length=255)
    language = models.CharField(
        max_length=10,
        choices=[("en", "English"), ("fr", "French"), ("es", "Spanish")],
        default="en"
    )
    slug = models.SlugField(unique=True)
    content = models.TextField()
    meta_title = models.CharField(
        max_length=255,
        blank=True
    )
    meta_description = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    scheduled_publish_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Schedule content update"
    )
    views = models.PositiveIntegerField(default=0)  # Count page views
    previous_versions = models.JSONField(
        default=list,
        blank=True,
        help_text="Stores older versions"
    )

    class Meta:
        unique_together = ("website", "slug")

    def is_scheduled(self):
        return self.scheduled_publish_date and self.scheduled_publish_date > timezone.now()

    def increment_views(self):
        self.views += 1
        self.save(update_fields=["views"])

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = WebsiteStaticPage.objects.get(pk=self.pk)
            if old_instance.content != self.content:
                self.previous_versions.append(
                    {
                        "content": old_instance.content,
                        "last_updated": old_instance.last_updated.isoformat(),
                    }
                )

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not is_new:  # Notify only for updates, not new pages
            send_mail(
                subject="Static Page Updated",
                message=f"The static page '{self.title}' was updated.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email for admin in User.objects.filter(is_superuser=True)],  # 🔥 Send to all superadmins
            )

    def __str__(self):
        return f"{self.website.name} - {self.title}"

# website/models.py
class WebsiteSettings(models.Model):
    """
    A model to store general website settings like domain URL and sender details.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='website_settings'
    )
    name = models.CharField(max_length=100)
    no_reply_email = models.EmailField()
    domain_url = models.URLField(
        max_length=200,
        help_text="The main domain of the website"
    )
    sender_name = models.CharField(
        max_length=100,
        help_text="Name of the sender (e.g., Company name)"
    )
    sender_email = models.EmailField(
        max_length=200,
        help_text="Sender's email address"
    )
    
    def __str__(self):
        return self.sender_name
