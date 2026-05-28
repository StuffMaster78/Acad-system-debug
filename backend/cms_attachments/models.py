"""
CMS Attachments
=================

Downloadable resources: templates, sample papers, guides, worksheets.
Each attachment is a first-class entity with:
- Its own SEO landing page (/resources/<slug>/)
- Embeddable in any blog post or service page via AttachmentReferenceBlock
- Five gate types (free / email / account / customer / paid)
- Download and conversion tracking
- Version management
- Ratings (no comments)
"""

from django.conf import settings
from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.search import index
from wagtail.snippets.models import register_snippet


ATTACHMENT_TYPE_CHOICES = [
    ("sample_essay", "Sample Essay/Paper"),
    ("template", "Template (fillable)"),
    ("outline", "Outline/Structure"),
    ("rubric", "Rubric/Grading Guide"),
    ("checklist", "Checklist"),
    ("worksheet", "Worksheet/Exercise"),
    ("cheat_sheet", "Cheat Sheet/Quick Reference"),
    ("guide", "Comprehensive Guide"),
    ("infographic", "Infographic"),
    ("study_guide", "Study Guide"),
    ("reference_list", "Reference List/Bibliography"),
    ("citation_examples", "Citation Examples (APA/MLA/etc)"),
    ("formatting_guide", "Formatting Guide"),
    ("case_study_template", "Case Study Template"),
    ("research_proposal_template", "Research Proposal Template"),
    ("thesis_template", "Thesis/Dissertation Template"),
    ("care_plan_template", "Nursing Care Plan Template"),
    ("soap_note_template", "SOAP Note Template"),
    ("other", "Other"),
]

ACADEMIC_LEVEL_CHOICES = [
    ("high_school", "High School"),
    ("undergraduate", "Undergraduate"),
    ("graduate", "Graduate/Masters"),
    ("phd", "PhD/Doctoral"),
    ("professional", "Professional"),
    ("general", "General/All Levels"),
]

FORMATTING_STYLE_CHOICES = [
    ("apa7", "APA 7th Edition"),
    ("apa6", "APA 6th Edition"),
    ("mla9", "MLA 9th Edition"),
    ("chicago", "Chicago/Turabian"),
    ("harvard", "Harvard"),
    ("ieee", "IEEE"),
    ("ama", "AMA"),
    ("vancouver", "Vancouver"),
    ("na", "Not Applicable"),
]

GATE_TYPE_CHOICES = [
    ("free", "Free — no requirement"),
    ("email", "Requires email signup"),
    ("account", "Requires user account"),
    ("customer", "Requires past order"),
    ("paid", "Premium — paid only"),
]

SCHEMA_TYPE_CHOICES = [
    ("DigitalDocument", "Digital Document"),
    ("LearningResource", "Learning Resource"),
    ("CreativeWork", "Creative Work"),
]


class AttachmentCategory(models.Model):
    """Groupings like 'Templates', 'Sample Papers', 'Study Guides'."""
    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="attachment_categories",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()
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
        verbose_name_plural = "Attachment Categories"

    def __str__(self):
        return self.name


class Attachment(index.Indexed, models.Model):
    """A downloadable file resource.

    Registered as a Wagtail Snippet so it's available in the
    AttachmentReferenceBlock chooser panel. Also has its own
    AttachmentLandingPage for SEO-indexable /resources/<slug>/ URLs.
    """

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    # --- Identity ---
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(max_length=500, blank=True)
    category = models.ForeignKey(
        AttachmentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
    )
    attachment_type = models.CharField(
        max_length=50,
        choices=ATTACHMENT_TYPE_CHOICES,
        default="template",
    )

    # --- File (via files_management) ---
    managed_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.PROTECT,
        related_name="attachment_uses",
        null=True,
        blank=True,
        help_text="The actual downloadable file",
    )
    preview_file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachment_previews",
        help_text="Preview image or first-page thumbnail",
    )

    # --- File metadata (cached from ManagedFile for display) ---
    file_format = models.CharField(max_length=20, blank=True)
    file_size_bytes = models.PositiveIntegerField(default=0)
    page_count = models.PositiveIntegerField(default=0)

    # --- Academic metadata ---
    academic_level = models.CharField(
        max_length=30,
        choices=ACADEMIC_LEVEL_CHOICES,
        default="general",
    )
    subject_area = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Nursing, Business, Psychology",
    )
    formatting_style = models.CharField(
        max_length=20,
        choices=FORMATTING_STYLE_CHOICES,
        default="na",
    )
    word_count = models.PositiveIntegerField(
        default=0,
        help_text="For sample essays/papers",
    )

    # --- Access control ---
    gate_type = models.CharField(
        max_length=20,
        choices=GATE_TYPE_CHOICES,
        default="free",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Only for 'paid' gate type",
    )

    # --- SEO ---
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    schema_type = models.CharField(
        max_length=30,
        choices=SCHEMA_TYPE_CHOICES,
        default="DigitalDocument",
    )

    # --- Graph relationships ---
    related_service = models.ForeignKey(
        "cms_service_pages.ServicePage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
    )

    # --- Authorship ---
    author = models.ForeignKey(
        "cms_authors.Author",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attachments",
    )
    author_credentials = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g., 'MSN, RN, 10 years nursing education'",
    )

    # --- Quality ---
    is_verified = models.BooleanField(
        default=False,
        help_text="Reviewed by editor, confirmed high quality",
    )
    is_featured = models.BooleanField(default=False)
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)

    # --- Usage metrics ---
    download_count = models.PositiveIntegerField(default=0)
    email_capture_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(
        default=0,
        help_text="Downloads that led to orders",
    )

    # --- Versioning ---
    version = models.CharField(max_length=20, default="1.0")
    superseded_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_versions",
    )

    # --- Lifecycle ---
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    review_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="When to review for accuracy (e.g., APA 6 → APA 7 transitions)",
    )

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("site"),
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
            FieldPanel("description"),
            FieldPanel("category"),
            FieldPanel("attachment_type"),
        ], heading="Identity"),
        MultiFieldPanel([
            FieldPanel("managed_file"),
            FieldPanel("preview_file"),
        ], heading="Files"),
        MultiFieldPanel([
            FieldPanel("academic_level"),
            FieldPanel("subject_area"),
            FieldPanel("formatting_style"),
            FieldPanel("word_count"),
        ], heading="Academic Metadata"),
        MultiFieldPanel([
            FieldPanel("gate_type"),
            FieldPanel("price"),
        ], heading="Access Control"),
        MultiFieldPanel([
            FieldPanel("meta_title"),
            FieldPanel("meta_description"),
            FieldPanel("schema_type"),
        ], heading="SEO"),
        MultiFieldPanel([
            FieldPanel("related_service"),
            FieldPanel("author"),
        ], heading="Relationships"),
        MultiFieldPanel([
            FieldPanel("is_verified"),
            FieldPanel("is_featured"),
            FieldPanel("version"),
            FieldPanel("superseded_by"),
            FieldPanel("status"),
            FieldPanel("review_due_date"),
        ], heading="Lifecycle"),
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
        index.SearchField("subject_area"),
        index.FilterField("site"),
        index.FilterField("attachment_type"),
        index.FilterField("status"),
        index.FilterField("gate_type"),
    ]

    class Meta:
        unique_together = ["site", "slug"]
        indexes = [
            models.Index(fields=["site", "status", "attachment_type"]),
            models.Index(fields=["site", "category", "status"]),
            models.Index(fields=["download_count"]),
        ]
        ordering = ["-is_featured", "-download_count", "-created_at"]

    def __str__(self):
        return self.title


class AttachmentLandingPage(Page):
    """SEO-indexable landing page for an attachment at /resources/<slug>/.

    The page is public and indexable even for gated attachments —
    only the download itself is gated, not the description page.
    """

    attachment = models.OneToOneField(
        Attachment,
        on_delete=models.PROTECT,
        related_name="landing_page",
    )

    content_panels = Page.content_panels + [
        FieldPanel("attachment"),
    ]

    subpage_types = []
    parent_page_types = ["cms_core.ResourceIndexPage"]

    api_fields = [
        APIField("attachment"),
    ]

    class Meta:
        verbose_name = "Attachment Landing Page"


class AttachmentDownload(models.Model):
    """Tracks every download event with attribution."""

    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="downloads",
    )

    # User identification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    session_id = models.CharField(max_length=255, blank=True)
    email = models.EmailField(
        blank=True,
        help_text="Captured email if gated by email",
    )

    # Source attribution
    source_page_url = models.URLField(
        blank=True,
        help_text="The page the user was on when they clicked download",
    )
    referrer = models.URLField(blank=True)

    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    country_code = models.CharField(max_length=2, blank=True)

    # Conversion tracking
    converted_to_order = models.BooleanField(default=False)
    order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["attachment", "created_at"]),
            models.Index(fields=["email"]),
        ]
        ordering = ["-created_at"]


class AttachmentRating(models.Model):
    """Star rating for an attachment. No comments — just rating."""

    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_id = models.CharField(max_length=255, blank=True)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attachment", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_attachment_rating_per_user",
            ),
        ]


class EmailGatedAccess(models.Model):
    """Email captures from gated downloads.
    Feeds into cms_newsletters for subscriber creation."""

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="email_captures",
    )
    email = models.EmailField()
    attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="email_captures",
    )

    # Consent
    consent_marketing = models.BooleanField(default=False)
    consent_newsletter = models.BooleanField(default=False)

    # Tracking
    download_count = models.PositiveIntegerField(default=1)
    last_download = models.DateTimeField(auto_now=True)

    # Conversion
    converted = models.BooleanField(default=False)
    conversion_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Source
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["site", "email"]
        indexes = [
            models.Index(fields=["site", "email"]),
            models.Index(fields=["site", "converted"]),
        ]

    def __str__(self):
        return f"{self.email} → {self.attachment.title}"