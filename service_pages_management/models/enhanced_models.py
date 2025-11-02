"""
Enhanced models for service pages - FAQs, Resources, CTAs, SEO.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField
from websites.models import Website
from django.contrib.auth import get_user_model

User = get_user_model()


class ServicePageFAQ(models.Model):
    """
    FAQs for service pages with Schema.org FAQPage support.
    """
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='faqs'
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    question_slug = models.SlugField(max_length=255, blank=True)
    display_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    # Schema.org properties
    upvote_count = models.PositiveIntegerField(default=0)
    accepted_answer = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['is_featured', 'display_order', 'question']
        verbose_name = "Service Page FAQ"
        verbose_name_plural = "Service Page FAQs"
    
    def __str__(self):
        return f"{self.question} - {self.service_page.title}"


class ServicePageResource(models.Model):
    """
    Resources linked to service pages (downloads, external links, etc.).
    """
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('download', 'Download'),
            ('link', 'External Link'),
            ('video', 'Video'),
            ('document', 'Document'),
        ],
        default='link'
    )
    display_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'title']
    
    def __str__(self):
        return f"{self.title} - {self.service_page.title}"


class ServicePageCTA(models.Model):
    """
    Call-to-Action blocks for service pages.
    """
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='ctas'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    button_text = models.CharField(max_length=100)
    button_url = models.URLField()
    style = models.CharField(
        max_length=20,
        choices=[
            ('primary', 'Primary'),
            ('secondary', 'Secondary'),
            ('success', 'Success'),
        ],
        default='primary'
    )
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.title} - {self.service_page.title}"


class ServicePageSEOMetadata(models.Model):
    """
    Enhanced SEO metadata for service pages with comprehensive
    Schema.org, Open Graph, and Twitter Card support.
    """
    service_page = models.OneToOneField(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='seo_metadata'
    )
    
    # Schema.org
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated keywords for SEO"
    )
    article_type = models.CharField(
        max_length=50,
        default='WebPage',
        choices=[
            ('WebPage', 'WebPage'),
            ('Service', 'Service'),
            ('Product', 'Product'),
            ('LocalBusiness', 'Local Business'),
        ],
        help_text="Schema.org type"
    )
    
    # Open Graph
    og_type = models.CharField(
        max_length=50,
        default='website',
        help_text="Open Graph type"
    )
    og_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="OG title (defaults to page title if empty)"
    )
    og_description = models.TextField(
        blank=True,
        help_text="OG description"
    )
    og_image = models.ImageField(
        upload_to='service_pages/og_images/',
        null=True,
        blank=True,
        help_text="OG image (1200x630px recommended)"
    )
    og_url = models.URLField(
        blank=True,
        help_text="Canonical URL for OG"
    )
    og_site_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Site name for OG"
    )
    
    # Twitter Card
    twitter_card_type = models.CharField(
        max_length=20,
        default='summary_large_image',
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary with Large Image'),
            ('app', 'App'),
            ('player', 'Player'),
        ]
    )
    twitter_title = models.CharField(max_length=255, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.ImageField(
        upload_to='service_pages/twitter_images/',
        null=True,
        blank=True,
        help_text="Twitter image (1200x675px recommended)"
    )
    twitter_site = models.CharField(
        max_length=100,
        blank=True,
        help_text="Twitter handle (e.g., @yourhandle)"
    )
    
    # Additional Schema.org
    schema_breadcrumb = JSONField(
        default=list,
        blank=True,
        help_text="BreadcrumbList schema data"
    )
    schema_organization = JSONField(
        default=dict,
        blank=True,
        help_text="Organization schema data"
    )
    schema_rating = JSONField(
        default=dict,
        blank=True,
        help_text="AggregateRating schema (if applicable)"
    )
    
    # Google-specific
    google_business_url = models.URLField(
        blank=True,
        help_text="Google Business Profile URL"
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Canonical URL for this page"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Service Page SEO Metadata"
        verbose_name_plural = "Service Page SEO Metadata"
    
    def __str__(self):
        return f"SEO Metadata for {self.service_page.title}"


class ServicePageEditHistory(models.Model):
    """
    Tracks edit history for service pages.
    """
    service_page = models.ForeignKey(
        'service_pages_management.ServicePage',
        on_delete=models.CASCADE,
        related_name='edit_history'
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    previous_content = models.TextField()
    current_content = models.TextField()
    changes_summary = models.TextField(blank=True)
    fields_changed = JSONField(default=list, blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-edited_at']
    
    def __str__(self):
        return f"{self.service_page.title} - Edited {self.edited_at}"

