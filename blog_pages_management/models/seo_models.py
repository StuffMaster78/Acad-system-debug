"""
Enhanced SEO models for Schema.org structured data,
Open Graph, Twitter Cards, and Google visibility.
"""
from django.db import models
from django.db.models import JSONField
from websites.models import Website
from django.utils import timezone


class BlogSEOMetadata(models.Model):
    """
    Comprehensive SEO metadata for blog posts including Schema.org,
    Open Graph, and Twitter Cards for maximum Google visibility.
    """
    blog = models.OneToOneField(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='seo_metadata'
    )
    
    # Schema.org Article markup (for Google)
    article_type = models.CharField(
        max_length=50,
        default='BlogPosting',
        help_text="Schema.org article type (BlogPosting, NewsArticle, etc.)"
    )
    article_section = models.CharField(
        max_length=255,
        blank=True,
        help_text="Article section for Schema.org"
    )
    keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated keywords for SEO"
    )
    article_published_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="ISO 8601 date for Schema.org"
    )
    article_modified_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="ISO 8601 date for Schema.org"
    )
    article_author_url = models.URLField(
        blank=True,
        help_text="Author page URL for Schema.org"
    )
    
    # Open Graph (for social sharing)
    og_type = models.CharField(
        max_length=50,
        default='article',
        help_text="Open Graph type"
    )
    og_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="OG title (defaults to blog title if empty)"
    )
    og_description = models.TextField(
        blank=True,
        help_text="OG description"
    )
    og_image = models.ImageField(
        upload_to='og_images/',
        null=True,
        blank=True,
        help_text="OG image (1200x630px recommended)"
    )
    og_image_alt = models.CharField(
        max_length=255,
        blank=True,
        help_text="OG image alt text"
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
    twitter_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Twitter title"
    )
    twitter_description = models.TextField(
        blank=True,
        help_text="Twitter description"
    )
    twitter_image = models.ImageField(
        upload_to='twitter_images/',
        null=True,
        blank=True,
        help_text="Twitter image (1200x675px recommended)"
    )
    twitter_site = models.CharField(
        max_length=100,
        blank=True,
        help_text="Twitter handle (e.g., @yourhandle)"
    )
    twitter_creator = models.CharField(
        max_length=100,
        blank=True,
        help_text="Twitter creator handle"
    )
    
    # Additional Schema.org properties
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
    google_news_keywords = models.CharField(
        max_length=500,
        blank=True,
        help_text="Google News keywords"
    )
    google_story = models.BooleanField(
        default=False,
        help_text="Enable Google AMP story format"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Blog SEO Metadata"
        verbose_name_plural = "Blog SEO Metadata"
    
    def __str__(self):
        return f"SEO Metadata for {self.blog.title}"


class FAQSchema(models.Model):
    """
    Enhanced FAQ model with Schema.org FAQPage markup
    for Google rich snippets and voice search optimization.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='faq_schemas'
    )
    question = models.CharField(
        max_length=500,
        help_text="FAQ question"
    )
    answer = models.TextField(
        help_text="FAQ answer (can include HTML)"
    )
    question_slug = models.SlugField(
        max_length=255,
        blank=True,
        help_text="URL-friendly slug for the question"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying FAQs"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured FAQs appear first"
    )
    
    # Schema.org properties
    upvote_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of upvotes (for Schema.org)"
    )
    accepted_answer = models.BooleanField(
        default=False,
        help_text="Mark as accepted answer"
    )
    author_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Author name for Schema.org"
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date FAQ was created"
    )
    date_modified = models.DateTimeField(
        auto_now=True,
        help_text="Last modification date"
    )
    
    class Meta:
        ordering = ['is_featured', 'display_order', 'question']
        verbose_name = "FAQ with Schema"
        verbose_name_plural = "FAQs with Schema"
    
    def save(self, *args, **kwargs):
        if not self.question_slug:
            from django.utils.text import slugify
            self.question_slug = slugify(self.question)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.question} - {self.blog.title}"


class AuthorSchema(models.Model):
    """
    Enhanced author information with Schema.org Person markup
    for Google Knowledge Graph and author attribution.
    """
    author = models.OneToOneField(
        'blog_pages_management.AuthorProfile',
        on_delete=models.CASCADE,
        related_name='schema_data'
    )
    
    # Schema.org Person properties
    given_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="First name"
    )
    family_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Last name"
    )
    job_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Job title/designation"
    )
    works_for = models.CharField(
        max_length=255,
        blank=True,
        help_text="Organization/Company name"
    )
    email = models.EmailField(
        blank=True,
        help_text="Email (for Schema.org)"
    )
    telephone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Phone number"
    )
    address = JSONField(
        default=dict,
        blank=True,
        help_text="Address object (street, city, state, country, postalCode)"
    )
    same_as = JSONField(
        default=list,
        blank=True,
        help_text="List of URLs (social profiles, website) for sameAs property"
    )
    knows_about = JSONField(
        default=list,
        blank=True,
        help_text="List of topics the author knows about"
    )
    award = models.TextField(
        blank=True,
        help_text="Awards or recognition"
    )
    
    # Google-specific
    google_author_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google+ profile ID or Google author page"
    )
    verified_mark = models.BooleanField(
        default=False,
        help_text="Verified author badge"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Author Schema Data"
        verbose_name_plural = "Author Schema Data"
    
    def __str__(self):
        return f"Schema for {self.author.name}"

