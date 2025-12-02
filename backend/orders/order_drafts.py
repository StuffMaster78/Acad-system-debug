"""
Order Drafts Model
Allows clients to save order drafts before final submission.
"""
from django.db import models
from django.conf import settings
from websites.models import Website


class OrderDraft(models.Model):
    """
    Saved draft of an order before final submission.
    Allows clients to build orders incrementally and convert to orders later.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_drafts'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_drafts',
        limit_choices_to={'role': 'client'}
    )
    
    # Order fields (mirror Order model)
    topic = models.CharField(max_length=500, blank=True)
    order_instructions = models.TextField(blank=True)
    number_of_pages = models.PositiveIntegerField(null=True, blank=True)
    number_of_slides = models.PositiveIntegerField(default=0)
    number_of_refereces = models.PositiveIntegerField(default=0)
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Foreign keys
    type_of_work = models.ForeignKey(
        'order_configs.TypeOfWork',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    english_type = models.ForeignKey(
        'order_configs.EnglishType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    preferred_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='draft_preferences',
        limit_choices_to={'role': 'writer'}
    )
    
    # Extra services
    extra_services = models.ManyToManyField(
        'pricing_configs.AdditionalService',
        blank=True,
        related_name='order_drafts'
    )
    
    # Quote/builder data
    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated price calculated from draft"
    )
    
    # Metadata
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional title for the draft"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this draft"
    )
    
    # Status
    is_quote = models.BooleanField(
        default=False,
        help_text="Whether this is a quote (not yet an order)"
    )
    converted_to_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_draft',
        help_text="The order this draft was converted to"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['client', 'website']),
            models.Index(fields=['is_quote', '-updated_at']),
        ]
        verbose_name = "Order Draft"
        verbose_name_plural = "Order Drafts"
    
    def __str__(self):
        return f"Draft #{self.id} - {self.client.email} - {self.topic[:50]}"
    
    def convert_to_order(self):
        """
        Convert this draft to an actual order.
        Returns the created Order instance.
        """
        from orders.models import Order
        
        order_data = {
            'website': self.website,
            'client': self.client,
            'topic': self.topic,
            'order_instructions': self.order_instructions,
            'number_of_pages': self.number_of_pages or 1,
            'number_of_slides': self.number_of_slides,
            'number_of_refereces': self.number_of_refereces,
            'deadline': self.deadline,
            'type_of_work': self.type_of_work,
            'english_type': self.english_type,
            'preferred_writer': self.preferred_writer,
        }
        
        order = Order.objects.create(**order_data)
        
        # Copy extra services
        if self.extra_services.exists():
            order.extra_services.set(self.extra_services.all())
        
        # Link draft to order
        self.converted_to_order = order
        self.save(update_fields=['converted_to_order'])
        
        return order

