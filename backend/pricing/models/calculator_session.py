"""
Pricing Calculator Session Model
Persists pricing calculations for users who haven't signed up yet.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json

User = settings.AUTH_USER_MODEL


class PricingCalculatorSession(models.Model):
    """
    Stores pricing calculations for anonymous or logged-in users.
    Allows users to proceed with order creation after signup.
    """
    session_key = models.CharField(
        max_length=40,
        db_index=True,
        help_text="Django session key or user identifier"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pricing_sessions',
        null=True,
        blank=True,
        help_text="User if logged in, null for anonymous"
    )
    
    # Order details used for calculation
    order_data = models.JSONField(
        help_text="Order details (paper_type, pages, deadline, etc.)"
    )
    
    # Calculated pricing
    calculated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Calculated total price"
    )
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Base price before adjustments"
    )
    adjustments = models.JSONField(
        default=dict,
        help_text="Price adjustments breakdown (urgency, level, etc.)"
    )
    discount_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Applied discount code if any"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Discount amount applied"
    )
    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final price after discounts"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this session expires (default 24 hours)"
    )
    converted_to_order = models.BooleanField(
        default=False,
        help_text="Whether this was converted to an actual order"
    )
    order_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Order ID if converted"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_key', 'expires_at']),
            models.Index(fields=['user', 'converted_to_order']),
        ]
    
    def __str__(self):
        user_label = self.user.username if self.user else self.session_key
        return f"Pricing Session - {user_label} - ${self.final_price}"
    
    def save(self, *args, **kwargs):
        """Set expiration date if not set."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if session has expired."""
        return timezone.now() > self.expires_at
    
    def mark_as_converted(self, order_id):
        """Mark this session as converted to an order."""
        from django.utils import timezone
        self.converted_to_order = True
        self.order_id = order_id
        self.save(update_fields=['converted_to_order', 'order_id'])
    
    @classmethod
    def create_session(cls, session_key, order_data, pricing_result, user=None, discount_code=None):
        """Create a new pricing session."""
        session = cls.objects.create(
            session_key=session_key,
            user=user,
            order_data=order_data,
            calculated_price=pricing_result.get('total_price', 0),
            base_price=pricing_result.get('base_price', 0),
            adjustments=pricing_result.get('adjustments', {}),
            discount_code=discount_code or '',
            discount_amount=pricing_result.get('discount_amount', 0),
            final_price=pricing_result.get('final_price', pricing_result.get('total_price', 0)),
            expires_at=timezone.now() + timedelta(hours=24)
        )
        return session
    
    @classmethod
    def get_active_session(cls, session_key, user=None):
        """Get active (non-expired, non-converted) session."""
        query = cls.objects.filter(
            expires_at__gt=timezone.now(),
            converted_to_order=False
        )
        
        if user:
            query = query.filter(user=user)
        else:
            query = query.filter(session_key=session_key)
        
        return query.order_by('-created_at').first()
    
    @classmethod
    def cleanup_expired(cls):
        """Delete expired sessions (run as periodic task)."""
        deleted_count, _ = cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        return deleted_count

