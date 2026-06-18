"""
CMS Service Pages
==================

Service pages (landing pages) are the bottom of the conversion funnel.
Each represents one monetized offering. 15-30 per tenant at maturity.

Their job: convert visitors into orders. Every block on the page
must earn its place toward conversion.

ServicePage is a Wagtail Page type with a deliberately smaller,
more opinionated block library than blog posts.
"""

from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.search import index
from wagtail.blocks import CharBlock

from cms_core.blocks import SERVICE_PAGE_BLOCKS


class ServicePageTemplate(models.TextChoices):
    STANDARD = "standard_service", "Standard service"
    ESSAY = "essay_service", "Essay / writing service"
    TECHNICAL = "technical_service", "Technical / data service"
    HEALTHCARE = "healthcare_service", "Healthcare / nursing service"
    ADMISSIONS = "admissions_service", "Admissions service"
    EDITING = "editing_service", "Editing / proofreading service"
    ONLINE_CLASS = "online_class_service", "Online class / coursework service"
    SEO_LANDING = "seo_landing_page", "SEO landing page"


class ServiceIndexPage(Page):
    """Container page for service pages. One per tenant site.
    Can live at /services/ or be hidden (service pages can also
    live directly under TenantHomePage for clean URLs)."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["cms_service_pages.ServicePage"]
    parent_page_types = ["cms_core.TenantHomePage"]

    api_fields = [APIField("intro")]

    class Meta:
        verbose_name = "Service Index Page"


class ServicePage(Page):
    """A single service / landing page. Bottom-of-funnel conversion.

    Funnel: BlogPostPage → ServicePage → Order.

    Block library is deliberately small and opinionated.
    If an editor wants something not in the library, evaluate
    whether the page actually needs it before building a new block.
    """

    # --- Service details ---
    template_key = models.CharField(
        max_length=50,
        choices=ServicePageTemplate.choices,
        default=ServicePageTemplate.STANDARD,
        help_text=(
            "Frontend template used by marketing sites such as GradeCrest. "
            "Controls layout emphasis while this page's copy remains editable."
        ),
    )
    service_category = models.ForeignKey(
        "cms_core.ServiceCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_pages",
    )
    pricing_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Starting price per page (USD)",
    )
    pricing_to = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum price per page (USD)",
    )
    turnaround_hours_fastest = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fastest turnaround in hours (e.g., 3 for 3-hour delivery)",
    )
    turnaround_hours_standard = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Standard turnaround in hours (e.g., 168 for 7-day delivery)",
    )

    # --- Conversion mechanics ---
    primary_cta_text = models.CharField(
        max_length=100,
        default="Order Now",
        help_text="Text on the primary call-to-action button",
    )
    primary_cta_url = models.CharField(
        max_length=255,
        default="/order/",
        help_text="Destination URL or path for the primary CTA",
    )
    show_aggregate_rating = models.BooleanField(
        default=True,
        help_text="Display aggregate rating from reviews in Schema.org markup",
    )

    # --- Trust / review ---
    reviewer = models.ForeignKey(
        "cms_authors.Author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_services",
        help_text="'Last reviewed by [Author] on [date]'",
    )

    # --- Hero override ---
    hero_headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Override the hero headline. Leave blank to use the static default.",
    )
    hero_sub = models.CharField(
        max_length=500,
        blank=True,
        help_text="Override the hero sub-headline. Leave blank to use the static default.",
    )

    # --- Sidebar bullets (editable by admins) ---
    includes_items = StreamField(
        [("item", CharBlock(label="Item", max_length=300))],
        use_json_field=True,
        blank=True,
        verbose_name="What's included",
        help_text="Each block is one bullet in the 'What's included' grid.",
    )
    delivers_items = StreamField(
        [("item", CharBlock(label="Item", max_length=300))],
        use_json_field=True,
        blank=True,
        verbose_name="What you receive",
        help_text="Each block is one bullet in the 'What you receive' checklist.",
    )
    who_for = models.TextField(
        blank=True,
        verbose_name="Who this is for",
        help_text="Short paragraph describing the target customer.",
    )

    # --- Content ---
    body = StreamField(
        SERVICE_PAGE_BLOCKS,
        use_json_field=True,
        blank=True,
    )

    # --- Freshness ---
    last_substantive_update = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Updated only when content substance changes. "
            "Drives Schema.org dateModified and freshness alerts."
        ),
    )
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="Social-sharing image for this service page. Overrides the tenant-level default OG image.",
    )

    # --- Panels ---
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_headline"),
                FieldPanel("hero_sub"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("template_key"),
                FieldPanel("service_category"),
                FieldPanel("pricing_from"),
                FieldPanel("pricing_to"),
                FieldPanel("turnaround_hours_fastest"),
                FieldPanel("turnaround_hours_standard"),
            ],
            heading="Service Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("includes_items"),
                FieldPanel("delivers_items"),
                FieldPanel("who_for"),
            ],
            heading="Service Highlights (sidebar bullets)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_cta_text"),
                FieldPanel("primary_cta_url"),
                FieldPanel("show_aggregate_rating"),
                FieldPanel("reviewer"),
            ],
            heading="Conversion",
        ),
        FieldPanel("body"),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("last_substantive_update"),
        FieldPanel("og_image"),
    ]

    # --- Subpage rules ---
    subpage_types = [] # Service pages have no children
    parent_page_types = ["cms_service_pages.ServiceIndexPage"]

    # --- Search indexing ---
    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.FilterField("service_category"),
        index.FilterField("first_published_at"),
    ]

    # --- API exposure ---
    api_fields = [
        APIField("hero_headline"),
        APIField("hero_sub"),
        APIField("template_key"),
        APIField("service_category"),
        APIField("pricing_from"),
        APIField("pricing_to"),
        APIField("turnaround_hours_fastest"),
        APIField("turnaround_hours_standard"),
        APIField("includes_items"),
        APIField("delivers_items"),
        APIField("who_for"),
        APIField("primary_cta_text"),
        APIField("primary_cta_url"),
        APIField("show_aggregate_rating"),
        APIField("reviewer"),
        APIField("body"),
        APIField("last_substantive_update"),
        APIField("og_image_url"),
    ]

    @property
    def og_image_url(self) -> str | None:
        if not self.og_image:
            return None
        try:
            return self.og_image.get_rendition("fill-1200x630").url
        except Exception:
            return None

    class Meta:
        verbose_name = "Service Page"
        verbose_name_plural = "Service Pages"

    def __str__(self):
        return self.title
