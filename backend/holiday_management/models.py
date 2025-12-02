"""
Holiday Management Models
Manages special days, holidays, and automated marketing features
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# CountryField not needed - using JSONField for countries list
from django.contrib.postgres.fields import JSONField

User = settings.AUTH_USER_MODEL


class SpecialDay(models.Model):
    """
    Represents a special day, holiday, or important event.
    Can be country-specific or international.
    """
    EVENT_TYPES = [
        ('holiday', _('Holiday')),
        ('special_day', _('Special Day')),
        ('anniversary', _('Anniversary')),
        ('seasonal', _('Seasonal Event')),
        ('cultural', _('Cultural Event')),
    ]
    
    PRIORITY_LEVELS = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    name = models.CharField(
        max_length=255,
        help_text=_("Name of the special day (e.g., 'Thanksgiving Day', 'Black Friday')")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of the special day")
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        default='holiday',
        help_text=_("Type of special day")
    )
    date = models.DateField(
        help_text=_("Date of the special day (for annual events, use any year)")
    )
    is_annual = models.BooleanField(
        default=True,
        help_text=_("Whether this event repeats annually")
    )
    is_international = models.BooleanField(
        default=False,
        help_text=_("Whether this is an international event")
    )
    countries = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of country codes where this event is observed (empty for international). Format: ['US', 'CA', 'GB']")
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text=_("Priority level for reminders")
    )
    
    # Reminder settings
    reminder_days_before = models.PositiveIntegerField(
        default=7,
        help_text=_("Number of days before the event to send reminder")
    )
    send_broadcast_reminder = models.BooleanField(
        default=True,
        help_text=_("Whether to remind admin to send broadcast message")
    )
    auto_generate_discount = models.BooleanField(
        default=False,
        help_text=_("Whether to automatically generate discount code")
    )
    
    # Discount settings
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Discount percentage (if auto-generating discount)")
    )
    discount_code_prefix = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Prefix for auto-generated discount code (e.g., 'THANKS2024')")
    )
    discount_valid_days = models.PositiveIntegerField(
        default=1,
        help_text=_("Number of days the discount is valid")
    )
    
    # Broadcast message template
    broadcast_message_template = models.TextField(
        blank=True,
        help_text=_("Template for broadcast message (can include {name}, {date}, etc.)")
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this special day is active")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_special_days'
    )

    class Meta:
        verbose_name = _('Special Day')
        verbose_name_plural = _('Special Days')
        ordering = ['date', 'priority']
        indexes = [
            models.Index(fields=['date', 'is_active']),
            models.Index(fields=['is_annual', 'is_active']),
            models.Index(fields=['priority', 'date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.date})"

    def get_date_for_year(self, year=None):
        """Get the date for a specific year (for annual events)."""
        if not self.is_annual:
            return self.date
        if year is None:
            year = timezone.now().year
        return self.date.replace(year=year)

    def is_upcoming(self, days_ahead=30):
        """Check if this event is upcoming within specified days."""
        today = timezone.now().date()
        event_date = self.get_date_for_year()
        
        # If event already passed this year and is annual, check next year
        if self.is_annual and event_date < today:
            event_date = self.get_date_for_year(today.year + 1)
        
        days_until = (event_date - today).days
        return 0 <= days_until <= days_ahead

    def should_send_reminder(self):
        """Check if reminder should be sent today."""
        if not self.send_broadcast_reminder or not self.is_active:
            return False
        
        today = timezone.now().date()
        event_date = self.get_date_for_year()
        
        # If event already passed this year and is annual, check next year
        if self.is_annual and event_date < today:
            event_date = self.get_date_for_year(today.year + 1)
        
        days_until = (event_date - today).days
        return days_until == self.reminder_days_before


class HolidayReminder(models.Model):
    """
    Tracks reminders sent for special days.
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('dismissed', _('Dismissed')),
        ('completed', _('Completed')),
    ]

    special_day = models.ForeignKey(
        SpecialDay,
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_date = models.DateField(
        help_text=_("Date when reminder was/will be sent")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    broadcast_sent = models.BooleanField(
        default=False,
        help_text=_("Whether broadcast message was sent")
    )
    discount_created = models.BooleanField(
        default=False,
        help_text=_("Whether discount code was created")
    )
    discount_code = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Generated discount code (if applicable)")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Admin notes about this reminder")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='holiday_reminders_received'
    )

    class Meta:
        verbose_name = _('Holiday Reminder')
        verbose_name_plural = _('Holiday Reminders')
        ordering = ['-reminder_date', '-created_at']
        unique_together = [('special_day', 'reminder_date')]
        indexes = [
            models.Index(fields=['status', 'reminder_date']),
            models.Index(fields=['special_day', 'reminder_date']),
        ]

    def __str__(self):
        return f"Reminder for {self.special_day.name} on {self.reminder_date}"


class HolidayDiscountCampaign(models.Model):
    """
    Tracks discount campaigns created for special days.
    """
    special_day = models.ForeignKey(
        SpecialDay,
        on_delete=models.CASCADE,
        related_name='discount_campaigns'
    )
    discount = models.ForeignKey(
        'discounts.Discount',
        on_delete=models.CASCADE,
        related_name='holiday_campaigns',
        help_text=_("The discount code created for this special day")
    )
    year = models.PositiveIntegerField(
        help_text=_("Year this campaign is for")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this campaign is currently active")
    )
    auto_generated = models.BooleanField(
        default=False,
        help_text=_("Whether this was auto-generated")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_holiday_campaigns'
    )

    class Meta:
        verbose_name = _('Holiday Discount Campaign')
        verbose_name_plural = _('Holiday Discount Campaigns')
        ordering = ['-year', '-created_at']
        unique_together = [('special_day', 'year')]
        indexes = [
            models.Index(fields=['special_day', 'year']),
            models.Index(fields=['is_active', 'year']),
        ]

    def __str__(self):
        return f"{self.special_day.name} {self.year} - {self.discount.code}"

