"""
Dashboard Configuration Models
Stores card configurations, colors, fonts, and content for role-specific dashboards
"""

from django.db import models
from websites.models import Website
from users.mixins import UserRole


class DashboardCardConfig(models.Model):
    """
    Configuration for dashboard cards - stores card appearance, data source, and role access
    """
    CARD_COLORS = (
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('purple', 'Purple'),
        ('orange', 'Orange'),
        ('red', 'Red'),
        ('pink', 'Pink'),
        ('indigo', 'Indigo'),
        ('teal', 'Teal'),
    )
    
    # Card identification
    card_key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique identifier for this card (e.g., 'total_orders', 'total_revenue')"
    )
    title = models.CharField(
        max_length=200,
        help_text="Card title/label"
    )
    description = models.TextField(
        blank=True,
        help_text="Card description or help text"
    )
    
    # Visual configuration
    icon = models.CharField(
        max_length=50,
        default="📊",
        help_text="Emoji or icon identifier"
    )
    color = models.CharField(
        max_length=20,
        choices=CARD_COLORS,
        default='blue',
        help_text="Card color theme"
    )
    
    # Data configuration
    data_source = models.CharField(
        max_length=200,
        help_text="API endpoint or data source path (e.g., 'dashboardData.total_orders')"
    )
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('number', 'Number'),
            ('currency', 'Currency'),
            ('percentage', 'Percentage'),
            ('text', 'Text'),
        ],
        default='number',
        help_text="Type of data to display"
    )
    
    # Role and access control
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of roles that can see this card (e.g., ['admin', 'superadmin'])"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dashboard_cards',
        help_text="Website-specific card (null = all websites)"
    )
    
    # Display configuration
    position = models.PositiveIntegerField(
        default=0,
        help_text="Display order (lower = first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this card is active"
    )
    badge_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Badge text to show in card footer (e.g., 'All time', 'Last 30 days')"
    )
    
    # Additional configuration
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional configuration (formatting options, calculations, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Card Configuration"
        verbose_name_plural = "Dashboard Card Configurations"
        ordering = ['position', 'title']
        indexes = [
            models.Index(fields=['card_key', 'is_active']),
            models.Index(fields=['website', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.card_key})"


class DashboardFontConfig(models.Model):
    """
    Font configuration for dashboards
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='dashboard_fonts',
        help_text="Website-specific font config (null = default for all)"
    )
    
    font_family = models.CharField(
        max_length=100,
        default="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        help_text="CSS font-family value"
    )
    font_url = models.URLField(
        blank=True,
        help_text="URL to load font from (e.g., Google Fonts)"
    )
    
    # Typography scales
    base_font_size = models.CharField(
        max_length=20,
        default="16px",
        help_text="Base font size"
    )
    card_value_font_size = models.CharField(
        max_length=50,
        default="clamp(24px, 3vw, 32px)",
        help_text="Card value font size (CSS clamp or fixed)"
    )
    card_label_font_size = models.CharField(
        max_length=20,
        default="13px",
        help_text="Card label font size"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard Font Configuration"
        verbose_name_plural = "Dashboard Font Configurations"
        unique_together = ['website']
    
    def __str__(self):
        return f"Font Config: {self.font_family} ({self.website.name if self.website else 'Default'})"

