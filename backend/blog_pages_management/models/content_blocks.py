"""
Content blocks for blogs - CTAs, Tables, Auto-inserted content sections.
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from websites.models import Website
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator


class CTABlock(models.Model):
    """
    Reusable Call-to-Action blocks that can be inserted into blog posts.
    Supports various CTA types for conversion optimization.
    """
    CTA_TYPE_CHOICES = [
        ('button', 'Button CTA'),
        ('banner', 'Banner CTA'),
        ('inline', 'Inline Text CTA'),
        ('popup', 'Popup/Modal CTA'),
        ('sidebar', 'Sidebar CTA'),
        ('footer', 'Footer CTA'),
        ('form', 'Form CTA'),
        ('download', 'Download CTA'),
        ('custom', 'Custom HTML'),
    ]
    
    CTA_STYLE_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info'),
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='cta_blocks'
    )
    name = models.CharField(
        max_length=255,
        help_text="Internal name for this CTA block"
    )
    cta_type = models.CharField(
        max_length=20,
        choices=CTA_TYPE_CHOICES,
        default='button'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="CTA headline/title"
    )
    description = models.TextField(
        blank=True,
        help_text="CTA description text"
    )
    button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Button/CTA text (e.g., 'Get Started', 'Download Now')"
    )
    button_url = models.URLField(
        blank=True,
        help_text="URL where the CTA links to"
    )
    style = models.CharField(
        max_length=20,
        choices=CTA_STYLE_CHOICES,
        default='primary'
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code (e.g., #FF5733)"
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for text"
    )
    custom_html = models.TextField(
        blank=True,
        help_text="Custom HTML for custom CTA type"
    )
    image = models.ImageField(
        upload_to='cta_images/',
        null=True,
        blank=True,
        help_text="Image for banner/popup CTAs"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this CTA is currently active"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying in lists"
    )
    conversion_goal = models.CharField(
        max_length=100,
        blank=True,
        help_text="Goal to track (e.g., 'order_placed', 'newsletter_signup')"
    )
    tracking_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Unique tracking ID for analytics"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['website', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.cta_type})"


class BlogCTAPlacement(models.Model):
    """
    Tracks where CTAs are placed within blog posts.
    Supports automatic and manual placement.
    """
    PLACEMENT_TYPE_CHOICES = [
        ('auto_top', 'Auto-insert at top'),
        ('auto_middle', 'Auto-insert in middle'),
        ('auto_bottom', 'Auto-insert at bottom'),
        ('after_paragraph', 'After specific paragraph'),
        ('after_heading', 'After specific heading'),
        ('manual', 'Manually placed'),
    ]
    
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='cta_placements'
    )
    cta_block = models.ForeignKey(
        CTABlock,
        on_delete=models.CASCADE,
        related_name='blog_placements'
    )
    placement_type = models.CharField(
        max_length=20,
        choices=PLACEMENT_TYPE_CHOICES,
        default='manual'
    )
    position = models.IntegerField(
        default=0,
        help_text="Position in content (paragraph number, heading index, etc.)"
    )
    is_active = models.BooleanField(default=True)
    display_conditions = JSONField(
        default=dict,
        blank=True,
        help_text="Conditions for showing this CTA (e.g., {'scroll_percent': 50})"
    )
    click_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['blog', 'cta_block', 'placement_type', 'position']
        indexes = [
            models.Index(fields=['blog', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.blog.title} - {self.cta_block.name} ({self.placement_type})"


class ContentBlockTemplate(models.Model):
    """
    Reusable content block templates (tables, info boxes, etc.)
    that can be auto-inserted into blog posts.
    """
    BLOCK_TYPE_CHOICES = [
        ('table', 'Data Table'),
        ('info_box', 'Info Box'),
        ('warning_box', 'Warning Box'),
        ('tip_box', 'Tip Box'),
        ('quote', 'Quote Block'),
        ('statistics', 'Statistics Block'),
        ('timeline', 'Timeline'),
        ('comparison', 'Comparison Table'),
        ('testimonial', 'Testimonial Block'),
        ('pricing_table', 'Pricing Table'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='content_block_templates'
    )
    name = models.CharField(max_length=255)
    block_type = models.CharField(
        max_length=20,
        choices=BLOCK_TYPE_CHOICES
    )
    content = models.TextField(
        help_text="HTML/template content for this block"
    )
    template_data = JSONField(
        default=dict,
        blank=True,
        help_text="JSON data for dynamic content (e.g., table rows)"
    )
    css_classes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom CSS classes"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.block_type})"


class BlogContentBlock(models.Model):
    """
    Links content blocks to specific blog posts at specific positions.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='content_blocks'
    )
    template = models.ForeignKey(
        ContentBlockTemplate,
        on_delete=models.CASCADE,
        related_name='blog_blocks'
    )
    position = models.IntegerField(
        help_text="Position in content (paragraph/heading index)"
    )
    auto_insert = models.BooleanField(
        default=False,
        help_text="Whether this was auto-inserted"
    )
    custom_data = JSONField(
        default=dict,
        blank=True,
        help_text="Blog-specific data overriding template data"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        indexes = [
            models.Index(fields=['blog', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.blog.title} - {self.template.name}"


class BlogEditHistory(models.Model):
    """
    Tracks all edits made to blog posts for version control and audit.
    """
    blog = models.ForeignKey(
        'blog_pages_management.BlogPost',
        on_delete=models.CASCADE,
        related_name='edit_history'
    )
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_edits'
    )
    previous_content = models.TextField(
        help_text="Previous version of content"
    )
    current_content = models.TextField(
        help_text="New version of content"
    )
    changes_summary = models.TextField(
        blank=True,
        help_text="Summary of changes made"
    )
    fields_changed = JSONField(
        default=list,
        blank=True,
        help_text="List of field names that were changed"
    )
    edit_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason for the edit"
    )
    edited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-edited_at']
        indexes = [
            models.Index(fields=['blog', 'edited_at']),
        ]
    
    def __str__(self):
        return f"{self.blog.title} - Edited {self.edited_at} by {self.edited_by}"

