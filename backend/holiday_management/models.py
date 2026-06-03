"""
Holiday Management Models
Manages special days, holidays, and automated marketing features
"""
import calendar
from datetime import date, timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL


def _easter_date(year: int) -> date:
    """Anonymous Gregorian Easter algorithm (Spencer Jones)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(114 + h + l - 7 * m, 31)
    return date(year, month, day + 1)


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

    # Seeded / floating-date support
    is_seeded = models.BooleanField(
        default=False,
        help_text=_(
            "Pre-seeded system holiday. Admins may only edit discount/reminder "
            "settings — name, date, and type are locked."
        ),
    )
    date_rule = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "Rule for floating annual dates. "
            "nth_weekday: {type, month, n, weekday, offset_days?} "
            "last_weekday: {type, month, weekday} "
            "easter: {type, offset_days?}"
        ),
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
        """Get the date for a specific year, resolving floating-date rules."""
        if not self.is_annual:
            return self.date
        if year is None:
            year = timezone.now().year

        if self.date_rule:
            return self._resolve_date_rule(year)

        try:
            return self.date.replace(year=year)
        except ValueError:
            # Feb 29 in a non-leap year — fall back to Feb 28
            return self.date.replace(year=year, day=28)

    def _resolve_date_rule(self, year: int) -> date:
        rule = self.date_rule or {}
        rule_type = rule.get("type")
        offset = int(rule.get("offset_days", 0))

        if rule_type == "nth_weekday":
            month   = int(rule["month"])
            n       = int(rule["n"])       # 1-based
            weekday = int(rule["weekday"]) # 0=Mon … 6=Sun
            first = date(year, month, 1)
            days_ahead = (weekday - first.weekday()) % 7
            first_occurrence = first + timedelta(days=days_ahead)
            result = first_occurrence + timedelta(weeks=n - 1)
            return result + timedelta(days=offset)

        if rule_type == "last_weekday":
            month   = int(rule["month"])
            weekday = int(rule["weekday"])
            last = date(year, month, calendar.monthrange(year, month)[1])
            days_back = (last.weekday() - weekday) % 7
            result = last - timedelta(days=days_back)
            return result + timedelta(days=offset)

        if rule_type == "easter":
            return _easter_date(year) + timedelta(days=offset)

        # Unknown rule — fall back to stored date's month/day
        try:
            return self.date.replace(year=year)
        except ValueError:
            return self.date.replace(year=year, day=28)

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

