# from core.models.base import BaseModel
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.core.mail import send_mail
from django.utils.text import slugify
import re  # Fix missing import
from django.utils.timezone import now  # Fix missing import
from django.contrib.postgres.fields import JSONField  # PostgreSQL JSON support
from django.conf import settings
from websites.models.websites import Website
from websites.models.static_pages import WebsiteStaticPage

User = settings.AUTH_USER_MODEL 


class WebsiteTermsAcceptance(models.Model):
    """
    Tracks which version of the Terms/Policies a user accepted per website.

    This is critical for legal/audit trails:
    - Which version was active?
    - When did the user accept it?
    - From which IP / device?
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="terms_acceptances",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="terms_acceptances",
    )
    static_page = models.ForeignKey(
        WebsiteStaticPage,
        on_delete=models.CASCADE,
        related_name="terms_acceptances",
        help_text="The static page (usually slug='terms') that was accepted.",
    )
    terms_version = models.PositiveIntegerField(
        help_text="Version number of the terms page when accepted."
    )
    accepted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user accepted the terms."
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which terms were accepted."
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent string at the time of acceptance."
    )

    class Meta:
        unique_together = ("website", "user", "static_page", "terms_version")
        indexes = [
            models.Index(fields=["website", "user"]),
            models.Index(fields=["website", "static_page", "terms_version"]),
        ]

    def __str__(self):
        return f"{self.user} accepted v{self.terms_version} for {self.website}"


class GuestAccessToken(models.Model):
    """
    Secure, scoped access token for guest clients.

    - We store only a hash of the raw token.
    - Scope can be limited to a single order or a lightweight guest dashboard.
    """

    SCOPE_ORDER = "order"
    SCOPE_DASHBOARD = "dashboard"

    SCOPE_CHOICES = [
        (SCOPE_ORDER, "Single Order"),
        (SCOPE_DASHBOARD, "Guest Dashboard"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="guest_tokens",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="guest_tokens",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="guest_tokens",
        help_text="Optional: limit this token to a single order.",
    )
    token_hash = models.CharField(
        max_length=128,
        unique=True,
        help_text="Hashed value of the raw guest access token.",
    )
    scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default=SCOPE_ORDER,
        help_text="Controls what the guest session can access.",
    )
    expires_at = models.DateTimeField(
        help_text="When this token stops being valid.",
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this token was last redeemed (for rotation / auditing).",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    created_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address that initiated this token.",
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User-agent string for additional auditing / anomaly detection.",
    )

    class Meta:
        indexes = [
            models.Index(fields=["website", "user"]),
            models.Index(fields=["website", "order"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"Guest token for {self.user} on {self.website} (scope={self.scope})"

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
    support_email = models.EmailField()
    from_email = models.EmailField()
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
    
    # Payment Settings
    manual_payment_requests_enabled = models.BooleanField(
        default=True,
        help_text="Allow writers to request manual payments outside of scheduled dates"
    )
    default_payment_schedule = models.CharField(
        max_length=20,
        choices=[
            ('bi-weekly', 'Bi-Weekly (Every 2 weeks)'),
            ('monthly', 'Monthly'),
        ],
        default='bi-weekly',
        help_text="Default payment schedule for new writers"
    )
    
    def __str__(self):
        return self.sender_name


class ExternalReviewLink(models.Model):
    """
    Stores external review site links (TrustPilot, Google Reviews, etc.) 
    where clients can rate and review the website, orders, and writers.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='external_review_links',
        help_text="Website this review link belongs to"
    )
    review_site_name = models.CharField(
        max_length=100,
        help_text="Name of the review site (e.g., TrustPilot, Google Reviews, Yelp)"
    )
    review_url = models.URLField(
        help_text="URL to the review page/profile on the external site"
    )
    review_type = models.CharField(
        max_length=50,
        choices=[
            ('website', 'Website Review'),
            ('order', 'Order Review'),
            ('writer', 'Writer Review'),
            ('general', 'General Review'),
        ],
        default='general',
        help_text="Type of review this link is for"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this review link is currently active and should be shown to clients"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which to display this link (lower numbers first)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or instructions for clients"
    )
    icon_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional icon/logo URL for the review site"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'review_site_name']
        verbose_name = "External Review Link"
        verbose_name_plural = "External Review Links"
    
    def __str__(self):
        return f"{self.review_site_name} - {self.get_review_type_display()} ({self.website.name})"
