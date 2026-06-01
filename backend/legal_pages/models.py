from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class DocumentType(models.TextChoices):
    TERMS_OF_SERVICE = "terms_of_service", "Terms of Service"
    PRIVACY_POLICY = "privacy_policy", "Privacy Policy"
    REFUND_POLICY = "refund_policy", "Refund Policy"
    COOKIE_POLICY = "cookie_policy", "Cookie Policy"
    ACCEPTABLE_USE_POLICY = "acceptable_use_policy", "Acceptable Use Policy"
    WRITER_AGREEMENT = "writer_agreement", "Writer Agreement"
    COPYRIGHT_POLICY = "copyright_policy", "Copyright Policy"


class HelpAudience(models.TextChoices):
    ALL = "all", "All users"
    CLIENT = "client", "Clients"
    WRITER = "writer", "Writers"
    STAFF = "staff", "Staff / Support"


# ────────────────────────────────────────────────────────────────────────────
# Legal documents
# ────────────────────────────────────────────────────────────────────────────

class LegalDocument(models.Model):
    """
    A versioned legal document (T&C, Privacy Policy, Refund Policy, etc.).

    Only one document per (website, doc_type) may be active at a time.
    Previous versions are kept for audit purposes.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="legal_documents",
    )
    doc_type = models.CharField(
        max_length=64,
        choices=DocumentType.choices,
        db_index=True,
    )
    title = models.CharField(max_length=255)
    content = models.TextField(
        help_text=(
            "Full HTML content of the document. "
            "Use the rich editor or paste HTML directly."
        )
    )
    version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Version label shown to users (e.g. 1.0, 2.1).",
    )
    effective_date = models.DateField(
        default=timezone.now,
        help_text="Date from which this version is in effect.",
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "Only one version per document type may be active. "
            "Activating this version automatically deactivates the previous one."
        ),
    )
    requires_re_acceptance = models.BooleanField(
        default=False,
        help_text=(
            "When True, existing users are prompted to re-accept "
            "this version on their next login."
        ),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_legal_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_date", "-created_at"]
        indexes = [
            models.Index(fields=["website", "doc_type", "is_active"]),
            models.Index(fields=["website", "doc_type", "effective_date"]),
        ]

    def __str__(self) -> str:
        status = "ACTIVE" if self.is_active else "archived"
        return f"{self.get_doc_type_display()} v{self.version} ({status})"

    def activate(self) -> None:
        """
        Mark this version as active and deactivate all other versions
        of the same document type for this website.
        """
        LegalDocument.objects.filter(
            website=self.website,
            doc_type=self.doc_type,
            is_active=True,
        ).exclude(pk=self.pk).update(is_active=False)

        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])


class UserAgreement(models.Model):
    """
    Records a user's acceptance of a specific legal document version.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="legal_agreements",
    )
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name="user_agreements",
    )
    agreed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "document")
        ordering = ["-agreed_at"]
        indexes = [models.Index(fields=["user", "agreed_at"])]

    def __str__(self) -> str:
        return f"{self.user} accepted {self.document} at {self.agreed_at}"


# ────────────────────────────────────────────────────────────────────────────
# Help center
# ────────────────────────────────────────────────────────────────────────────

class HelpCategory(models.Model):
    """
    A group of related help articles (e.g. "Getting started", "Payments", "Writers").
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="help_categories",
    )
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lucide icon name (e.g. 'book-open', 'credit-card', 'users').",
    )
    audience = models.CharField(
        max_length=20,
        choices=HelpAudience.choices,
        default=HelpAudience.ALL,
        db_index=True,
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "slug")
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title


class HelpArticle(models.Model):
    """
    A single help article or user guide.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="help_articles",
    )
    category = models.ForeignKey(
        HelpCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text="One-line summary shown in category listings.",
    )
    content = models.TextField(
        help_text=(
            "Full HTML content of the article. "
            "Use headings (h2/h3), paragraphs, ordered/unordered lists, "
            "and <strong>/<em> for emphasis."
        )
    )
    audience = models.CharField(
        max_length=20,
        choices=HelpAudience.choices,
        default=HelpAudience.ALL,
        db_index=True,
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured articles appear on the help center home page.",
    )
    is_published = models.BooleanField(default=False, db_index=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_help_articles",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="updated_help_articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "slug")
        ordering = ["order", "title"]
        indexes = [
            models.Index(fields=["website", "is_published", "audience"]),
            models.Index(fields=["website", "category", "order"]),
        ]

    def __str__(self) -> str:
        status = "" if self.is_published else "draft"
        return f"[{status}] {self.title}"
