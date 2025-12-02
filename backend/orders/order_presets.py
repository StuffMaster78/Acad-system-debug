"""
Order Presets Model
Allows clients to save reusable order presets with default preferences.
"""
from django.db import models
from django.conf import settings
from websites.models import Website


class OrderPreset(models.Model):
    """
    Reusable order presets for clients.
    Stores preferred style, formatting, referencing, tone, etc.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_presets'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_presets',
        limit_choices_to={'role': 'client'}
    )
    
    # Preset name
    name = models.CharField(
        max_length=255,
        help_text="Name for this preset (e.g., 'Academic Essay', 'Business Report')"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of when to use this preset"
    )
    
    # Default preferences
    default_type_of_work = models.ForeignKey(
        'order_configs.TypeOfWork',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default type of work"
    )
    default_english_type = models.ForeignKey(
        'order_configs.EnglishType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default English style"
    )
    default_spacing = models.CharField(
        max_length=10,
        blank=True,
        help_text="Default spacing (single, double, etc.)"
    )
    default_number_of_refereces = models.PositiveIntegerField(
        default=0,
        help_text="Default number of references"
    )
    
    # Preferred writer
    preferred_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preset_preferences',
        limit_choices_to={'role': 'writer'}
    )
    
    # Default extra services
    default_extra_services = models.ManyToManyField(
        'pricing_configs.AdditionalService',
        blank=True,
        related_name='order_presets'
    )
    
    # Style preferences (stored as JSON for flexibility)
    style_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Style preferences: tone, formatting, citation style, etc."
    )
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this preset has been used"
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this preset was last used"
    )
    
    # Active status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this preset is active and available"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default preset for the client"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-usage_count', '-updated_at']
        indexes = [
            models.Index(fields=['client', 'website', 'is_active']),
            models.Index(fields=['is_default', 'client']),
        ]
        verbose_name = "Order Preset"
        verbose_name_plural = "Order Presets"
    
    def __str__(self):
        return f"{self.name} - {self.client.email}"
    
    def apply_to_draft(self, draft):
        """
        Apply this preset's defaults to an OrderDraft.
        """
        if self.default_type_of_work:
            draft.type_of_work = self.default_type_of_work
        if self.default_english_type:
            draft.english_type = self.default_english_type
        if self.default_spacing:
            draft.spacing = self.default_spacing
        if self.default_number_of_refereces:
            draft.number_of_refereces = self.default_number_of_refereces
        if self.preferred_writer:
            draft.preferred_writer = self.preferred_writer
        
        # Apply extra services
        if self.default_extra_services.exists():
            draft.extra_services.set(self.default_extra_services.all())
        
        draft.save()
        
        # Increment usage
        self.usage_count += 1
        self.last_used_at = models.timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])
        
        return draft
    
    def apply_to_order(self, order):
        """
        Apply this preset's defaults to an Order.
        """
        if self.default_type_of_work:
            order.type_of_work = self.default_type_of_work
        if self.default_english_type:
            order.english_type = self.default_english_type
        if self.default_spacing:
            order.spacing = self.default_spacing
        if self.default_number_of_refereces:
            order.number_of_refereces = self.default_number_of_refereces
        if self.preferred_writer:
            order.preferred_writer = self.preferred_writer
        
        # Apply extra services
        if self.default_extra_services.exists():
            order.extra_services.set(self.default_extra_services.all())
        
        order.save()
        
        # Increment usage
        from django.utils import timezone
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])
        
        return order

