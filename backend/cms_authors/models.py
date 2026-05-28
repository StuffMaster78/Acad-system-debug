"""
CMS Authors
=============

Real people with verifiable credentials. Non-negotiable per 2026 strategy.
No `is_fake` flag — every author is real or doesn't exist in this system.

Author is a Wagtail Snippet (for chooser panels in blog/service editors).
AuthorPage is a Wagtail Page (for public-facing /authors/<slug>/ profiles).
"""

from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class Author(index.Indexed, models.Model):
    """A real, credentialed content author.

    Each Author is scoped to a Wagtail Site (tenant).
    One real person can have Author records on multiple sites,
    each with a site-specific bio/positioning.
    """

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="authors",
    )

    # Identity
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    bio = models.TextField(
        help_text="Public biography — displayed on author profile page"
    )
    profile_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Credentials — real and verifiable
    credentials = models.CharField(
        max_length=255,
        blank=True,
        help_text="Displayed credentials, e.g. 'MSN, RN, CCRN'",
    )
    degrees = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'List of degrees: [{"degree": "MSN", "institution": "Johns Hopkins", '
            '"year": 2018, "verified": true}]'
        ),
    )
    licenses = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'List of professional licenses: [{"license": "RN", "state": "MD", '
            '"number": "R12345", "expires": "2027-06"}]'
        ),
    )
    areas_of_expertise = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated areas, e.g. 'Pediatric Nursing, Care Plans, EBP'",
    )
    years_experience = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Years of professional experience",
    )

    # External identity links (for E-E-A-T / sameAs in Schema.org)
    linkedin_url = models.URLField(blank=True)
    orcid_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="ORCID identifier, e.g. 0000-0002-1825-0097",
    )
    google_scholar_url = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=100, blank=True)

    # Role
    ROLE_CHOICES = [
        ("writer", "Writer"),
        ("senior_writer", "Senior Writer"),
        ("editor", "Editor"),
        ("subject_matter_expert", "Subject Matter Expert"),
        ("clinical_reviewer", "Clinical Reviewer"),
    ]
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="writer",
    )

    # Contact (internal, not public)
    contact_email = models.EmailField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    show_publicly = models.BooleanField(
        default=True,
        help_text="Show on the public author index page",
    )
    display_order = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("site"),
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("slug"),
                FieldPanel("profile_photo"),
                FieldPanel("bio"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("credentials"),
                FieldPanel("degrees"),
                FieldPanel("licenses"),
                FieldPanel("areas_of_expertise"),
                FieldPanel("years_experience"),
                FieldPanel("role"),
            ],
            heading="Credentials & Role",
        ),
        MultiFieldPanel(
            [
                FieldPanel("linkedin_url"),
                FieldPanel("orcid_id"),
                FieldPanel("google_scholar_url"),
                FieldPanel("personal_website"),
                FieldPanel("twitter_handle"),
            ],
            heading="External Identity Links",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_email"),
                FieldPanel("is_active"),
                FieldPanel("show_publicly"),
                FieldPanel("display_order"),
            ],
            heading="Settings",
        ),
    ]

    search_fields = [
        index.SearchField("name"),
        index.SearchField("bio"),
        index.SearchField("areas_of_expertise"),
        index.FilterField("site"),
        index.FilterField("is_active"),
        index.FilterField("role"),
    ]

    class Meta:
        unique_together = ["site", "slug"]
        ordering = ["display_order", "name"]

    def __str__(self):
        suffix = f" ({self.credentials})" if self.credentials else ""
        return f"{self.name}{suffix}"

    def get_same_as_links(self):
        """Return list of external identity URLs for Schema.org sameAs."""
        links = []
        if self.linkedin_url:
            links.append(self.linkedin_url)
        if self.orcid_id:
            links.append(f"https://orcid.org/{self.orcid_id}")
        if self.google_scholar_url:
            links.append(self.google_scholar_url)
        if self.personal_website:
            links.append(self.personal_website)
        if self.twitter_handle:
            handle = self.twitter_handle.lstrip("@")
            links.append(f"https://x.com/{handle}")
        return links


class AuthorPage(Page):
    """Public-facing author profile page at /authors/<slug>/.

    The Author snippet carries all the data.
    AuthorPage is just the Wagtail Page shell that makes it:
    - URL-routable
    - Indexable by search engines
    - Part of the page tree
    - Servable via Wagtail API v2
    """

    author = models.OneToOneField(
        Author,
        on_delete=models.PROTECT,
        related_name="profile_page",
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
    ]

    subpage_types = []  # Author pages have no children
    parent_page_types = ["cms_core.AuthorIndexPage"]

    api_fields = [
        APIField("author"),
    ]

    class Meta:
        verbose_name = "Author Profile Page"

    def get_context(self, request):
        """Add the author's published content to context."""
        context = super().get_context(request)

        # Get blog posts by this author on this site
        try:
            from cms_blog.models import BlogPostPage

            context["blog_posts"] = (
                BlogPostPage.objects.live()
                .filter(primary_author=self.author)
                .order_by("-first_published_at")[:20]
            )
        except ImportError:
            context["blog_posts"] = []

        return context