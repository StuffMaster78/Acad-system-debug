"""
CMS Core Models
================

Base page types, shared snippets, slug history, and tenant utilities.
Every other CMS app depends on this.
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.search import index
from wagtail.snippets.models import register_snippet


# ===========================================================================
# BASE PAGE TYPES
# ===========================================================================

class TenantHomePage(Page):
    """Root page for each tenant's page tree.

    Tree structure:
        Root Page (Wagtail internal)
        ├── NurseMyGrade Home (TenantHomePage)
        ├── GradeCrest Home (TenantHomePage)
        └── EssayManiacs Home (TenantHomePage)
    """
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = [
        "cms_blog.BlogIndexPage",
        "cms_service_pages.ServiceIndexPage",
        "cms_core.AuthorIndexPage",
        "cms_core.ResourceIndexPage",
    ]
    parent_page_types = ["wagtailcore.Page"]  # Only under Wagtail root

    api_fields = [
        APIField("intro"),
    ]

    class Meta:
        verbose_name = "Tenant Home Page"


class AuthorIndexPage(Page):
    """Container page listing all authors for a tenant. /authors/"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["cms_authors.AuthorPage"]
    parent_page_types = ["cms_core.TenantHomePage"]

    api_fields = [APIField("intro")]

    class Meta:
        verbose_name = "Author Index Page"


class ResourceIndexPage(Page):
    """Container page listing downloadable resources. /resources/"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["cms_attachments.AttachmentLandingPage"]
    parent_page_types = ["cms_core.TenantHomePage"]

    api_fields = [APIField("intro")]

    class Meta:
        verbose_name = "Resource Index Page"


# ===========================================================================
# SNIPPETS — tenant-scoped categories and tags
# ===========================================================================

class BlogCategory(index.Indexed, models.Model):
    """Blog post category. Tenant-scoped via site FK."""
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="blog_categories",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="SEO title for category page",
    )
    meta_description = models.TextField(
        blank=True,
        max_length=160,
        help_text="SEO description for category page",
    )
    display_order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("site"),
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("meta_title"),
        FieldPanel("meta_description"),
        FieldPanel("display_order"),
        FieldPanel("is_featured"),
        FieldPanel("is_active"),
    ]

    search_fields = [
        index.SearchField("name"),
        index.FilterField("site"),
        index.FilterField("is_active"),
    ]

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["-is_featured", "display_order", "name"]
        verbose_name_plural = "Blog Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    """Blog post tag. Tenant-scoped."""
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="blog_tags",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)

    panels = [
        FieldPanel("site"),
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    """Service page category (e.g., Nursing, Business, General). Tenant-scoped."""
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="service_categories",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    panels = [
        FieldPanel("site"),
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("display_order"),
    ]

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["display_order", "name"]
        verbose_name_plural = "Service Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ===========================================================================
# SLUG HISTORY — for automatic 301 redirects
# ===========================================================================

class SlugHistory(models.Model):
    """Tracks slug changes across all content types.
    Used by wagtail.contrib.redirects or a custom redirect middleware
    to auto-create 301s when slugs change."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    old_slug = models.SlugField(max_length=255, db_index=True)
    new_slug = models.SlugField(max_length=255)

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="slug_history",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["site", "old_slug"]),
            models.Index(fields=["content_type", "object_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.old_slug} → {self.new_slug} ({self.site})"


# ===========================================================================
# RESERVED SLUGS — per-tenant registry
# ===========================================================================

class ReservedSlug(models.Model):
    """Slugs that the frontend owns and CMS pages cannot use.
    e.g., /about/, /contact/, /login/, /order/, /account/"""
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="reserved_slugs",
    )
    slug = models.SlugField(max_length=255)
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Why this slug is reserved (e.g., 'Frontend about page')",
    )

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["slug"]

    def __str__(self):
        return f"{self.slug} (reserved on {self.site})"


# ===========================================================================
# PER-SITE SETTINGS
# ===========================================================================

@register_setting
class TenantSEOSettings(BaseSiteSetting):
    """Per-tenant SEO and branding configuration.
    Accessible via TenantSEOSettings.for_site(site) in templates and views."""

    default_citation_style = models.CharField(
        max_length=20,
        choices=[
            ("apa7", "APA 7th Edition"),
            ("mla9", "MLA 9th Edition"),
            ("chicago", "Chicago / Turabian"),
            ("none", "No formal citations"),
        ],
        default="apa7",
    )
    default_og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Default Open Graph image for pages without a featured image",
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="GA4 Measurement ID (G-XXXXXXXXXX)",
    )
    gsc_property_url = models.URLField(
        blank=True,
        help_text="Google Search Console property URL",
    )
    ga4_property_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="GA4 property ID (numeric)",
    )
    schema_org_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Organization name for Schema.org",
    )
    schema_org_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Organization logo for Schema.org",
    )

    panels = [
        FieldPanel("default_citation_style"),
        FieldPanel("default_og_image"),
        FieldPanel("google_analytics_id"),
        FieldPanel("gsc_property_url"),
        FieldPanel("ga4_property_id"),
        FieldPanel("schema_org_name"),
        FieldPanel("schema_org_logo"),
    ]

    class Meta:
        verbose_name = "Tenant SEO Settings"