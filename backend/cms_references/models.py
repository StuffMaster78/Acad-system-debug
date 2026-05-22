"""
CMS References
================

External sources cited in blog posts. Dual-mode:
- sources_list (default): flat list at bottom, EssayPro pattern
- formal citations (opt-in): inline markers with APA 7 / MLA / Chicago formatting

References are tenant-scoped. One Reference can be cited by many blog posts.
"""

from django.conf import settings
from django.db import models

from wagtail.search import index
from wagtail.snippets.models import register_snippet


REFERENCE_TYPE_CHOICES = [
    ("journal_article", "Peer-reviewed journal article"),
    ("book", "Book"),
    ("book_chapter", "Book chapter"),
    ("website", "Website / web article"),
    ("government_publication", "Government publication"),
    ("professional_organization", "Professional organization document"),
    ("clinical_guideline", "Clinical practice guideline"),
    ("news_article", "News article"),
    ("report", "Industry / research report"),
    ("thesis", "Thesis / dissertation"),
    ("conference_paper", "Conference paper"),
    ("other", "Other"),
]

QUALITY_TIER_CHOICES = [
    ("tier_1", "Peer-reviewed primary research"),
    ("tier_2", "Clinical guideline / professional org"),
    ("tier_3", "Authoritative website (.gov, .edu, established org)"),
    ("tier_4", "Reputable secondary source"),
    ("tier_5", "Other / general"),
]


@register_snippet
class ReferenceTag(models.Model):
    """Tags for organizing references (e.g., 'evidence-based-practice',
    'patient-safety', 'pediatric')."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_snippet
class Reference(index.Indexed, models.Model):
    """An external source cited in content.

    Tenant-scoped — each tenant maintains its own reference library.
    One Reference can be cited by many blog posts via the Citation model.
    """

    site = models.ForeignKey(
        "wagtailcore.Site",
        on_delete=models.CASCADE,
        related_name="references",
    )

    # --- Bibliographic identity ---
    reference_type = models.CharField(
        max_length=30,
        choices=REFERENCE_TYPE_CHOICES,
        default="website",
    )
    title = models.CharField(max_length=500)
    authors = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'List of author dicts: '
            '[{"family": "Smith", "given": "J.", "middle": "A."}]'
        ),
    )
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    publication_month = models.PositiveSmallIntegerField(null=True, blank=True)

    # --- Source-specific fields ---
    journal_name = models.CharField(max_length=255, blank=True)
    journal_volume = models.CharField(max_length=20, blank=True)
    journal_issue = models.CharField(max_length=20, blank=True)
    pages = models.CharField(
        max_length=20, blank=True,
        help_text="e.g., '234-251'",
    )
    publisher = models.CharField(max_length=255, blank=True)
    publisher_location = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)

    # --- Identifiers ---
    doi = models.CharField(
        max_length=255, blank=True, db_index=True,
        help_text="Digital Object Identifier (the gold standard)",
    )
    isbn = models.CharField(max_length=20, blank=True)
    pmid = models.CharField(
        max_length=20, blank=True,
        help_text="PubMed ID — especially relevant for nursing content",
    )
    issn = models.CharField(max_length=20, blank=True)

    # --- URLs and link rot protection ---
    url = models.URLField(max_length=500, blank=True)
    url_archived = models.URLField(
        max_length=500, blank=True,
        help_text="Wayback Machine snapshot URL — auto-captured on add",
    )
    is_url_dead = models.BooleanField(default=False)
    last_verified = models.DateTimeField(
        null=True, blank=True,
        help_text="Last time the URL was verified as reachable",
    )

    # --- Access and trust ---
    is_open_access = models.BooleanField(default=False)
    is_peer_reviewed = models.BooleanField(default=False)
    is_verified = models.BooleanField(
        default=False,
        help_text="Reviewed and confirmed as credible by an editor",
    )
    quality_tier = models.CharField(
        max_length=20,
        choices=QUALITY_TIER_CHOICES,
        blank=True,
    )

    # --- Tags ---
    tags = models.ManyToManyField(
        ReferenceTag,
        blank=True,
        related_name="references",
    )

    # --- Usage tracking ---
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Cached count of blog posts citing this reference",
    )

    # --- Internal notes ---
    internal_notes = models.TextField(
        blank=True,
        help_text="Internal-only notes — never displayed publicly",
    )

    # --- Metadata ---
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_references",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Wagtail admin ---
    panels = [
        # Defined in wagtail_hooks.py via SnippetViewSet for proper layout
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("journal_name"),
        index.SearchField("organization"),
        index.FilterField("site"),
        index.FilterField("reference_type"),
        index.FilterField("is_verified"),
        index.FilterField("quality_tier"),
    ]

    class Meta:
        indexes = [
            models.Index(fields=["site", "reference_type"]),
            models.Index(fields=["doi"]),
            models.Index(fields=["pmid"]),
            models.Index(fields=["site", "is_verified"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        year = f" ({self.publication_year})" if self.publication_year else ""
        return f"{self.title}{year}"

    @property
    def display_url(self):
        """Return the best available URL — prefer live, fall back to archive."""
        if self.url and not self.is_url_dead:
            return self.url
        if self.url_archived:
            return self.url_archived
        return self.url or ""

    @property
    def formatted_authors(self):
        """Format authors list for display.
        Returns: 'Smith, J. A., & Jones, B.' (APA-style default)"""
        if not self.authors:
            return ""
        parts = []
        for author in self.authors:
            family = author.get("family", "")
            given = author.get("given", "")
            middle = author.get("middle", "")
            initials = given
            if middle:
                initials = f"{given} {middle}"
            parts.append(f"{family}, {initials}".strip(", "))
        if len(parts) <= 2:
            return " & ".join(parts)
        return ", ".join(parts[:-1]) + f", & {parts[-1]}"


class Citation(models.Model):
    """A specific use of a Reference in a specific BlogPost.

    For sources_list mode: one Citation per source in the list.
    For formal mode: one Citation per reference, with inline markers
    in the body pointing to the citation's position.
    """

    blog_post = models.ForeignKey(
        "cms_blog.BlogPostPage",
        on_delete=models.CASCADE,
        related_name="citations",
    )
    reference = models.ForeignKey(
        Reference,
        on_delete=models.PROTECT,
        related_name="citations",
    )

    # Position in the reference list (1-based ordering)
    position = models.PositiveSmallIntegerField(
        help_text="Order in the references list (1, 2, 3...)",
    )

    # Optional: specific page/section being cited
    page = models.CharField(
        max_length=50, blank=True,
        help_text="e.g., 'pp. 23-25'",
    )

    # Internal note (never displayed publicly)
    editor_note = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["blog_post", "reference"]
        ordering = ["position"]

    def __str__(self):
        return f"[{self.position}] {self.reference.title} in {self.blog_post.title}"