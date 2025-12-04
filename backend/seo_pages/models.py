"""
SEO Landing Pages model for custom SEO-optimized landing pages.
"""
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from websites.models import Website

User = settings.AUTH_USER_MODEL


class SeoPage(models.Model):
    """
    SEO-optimized landing page with block-based content.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='seo_pages',
        help_text="Website this SEO page belongs to"
    )
    title = models.CharField(
        max_length=255,
        help_text="Page title (used in <h1> and meta title)"
    )
    slug = models.SlugField(
        max_length=255,
        db_index=True,
        help_text="URL slug (e.g., 'best-essay-writing-service')"
    )
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="SEO meta title (defaults to title if empty)"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="SEO meta description"
    )
    blocks = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of content blocks (paragraph, heading, image, CTA, etc.)"
    )
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this page is published and publicly accessible"
    )
    publish_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this page was published"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_seo_pages',
        help_text="User who created this page"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_seo_pages',
        help_text="User who last updated this page"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
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
    
    class Meta:
        unique_together = ['website', 'slug']
        indexes = [
            models.Index(fields=['website', 'slug', 'is_published']),
            models.Index(fields=['website', 'is_published', 'publish_date']),
        ]
        ordering = ['-publish_date', '-created_at']
    
    def __str__(self):
        return f"{self.website.name}: {self.title}"
    
    def get_meta_title(self):
        """Returns meta_title if set, otherwise title."""
        return self.meta_title or self.title

