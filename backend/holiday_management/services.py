"""
Holiday Management Services
"""
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django_countries import countries
from .models import SpecialDay, HolidayReminder, HolidayDiscountCampaign

User = get_user_model()


class HolidayReminderService:
    """Service for managing holiday reminders."""
    
    @staticmethod
    def get_upcoming_special_days(days_ahead=30, country_code=None):
        """Get upcoming special days within specified days."""
        today = timezone.now().date()
        end_date = today + timezone.timedelta(days=days_ahead)
        
        query = Q(is_active=True)
        
        # Filter by country if specified
        if country_code:
            # For JSONField, use __contains with the value directly (not in a list)
            query &= (Q(is_international=True) | Q(countries__contains=country_code))
        else:
            query &= Q(is_international=True)
        
        special_days = SpecialDay.objects.filter(query).distinct()
        
        upcoming = []
        for day in special_days:
            event_date = day.get_date_for_year()
            
            # If annual and passed this year, check next year
            if day.is_annual and event_date < today:
                event_date = day.get_date_for_year(today.year + 1)
            
            if today <= event_date <= end_date:
                upcoming.append(day)
        
        return sorted(upcoming, key=lambda x: x.get_date_for_year())
    
    @staticmethod
    def check_and_create_reminders():
        """Check for special days that need reminders and create them."""
        today = timezone.now().date()
        reminders_created = []
        
        # Get all active special days
        special_days = SpecialDay.objects.filter(
            is_active=True,
            send_broadcast_reminder=True
        )
        
        for special_day in special_days:
            if special_day.should_send_reminder():
                # Check if reminder already exists
                reminder_date = today
                reminder, created = HolidayReminder.objects.get_or_create(
                    special_day=special_day,
                    reminder_date=reminder_date,
                    defaults={
                        'status': 'pending'
                    }
                )
                
                if created:
                    reminders_created.append(reminder)
        
        return reminders_created
    
    @staticmethod
    def get_pending_reminders():
        """Get all pending reminders."""
        return HolidayReminder.objects.filter(
            status='pending'
        ).select_related('special_day', 'sent_to').order_by('reminder_date')
    
    @staticmethod
    def mark_reminder_sent(reminder_id, user):
        """Mark a reminder as sent."""
        reminder = HolidayReminder.objects.get(id=reminder_id)
        reminder.status = 'sent'
        reminder.sent_to = user
        reminder.save()
        return reminder


class HolidayDiscountService:
    """Service for managing holiday discount campaigns."""
    
    @staticmethod
    def generate_discount_code(special_day, year=None):
        """Generate a discount code for a special day."""
        if year is None:
            year = timezone.now().year
        
        # Use prefix if provided, otherwise use event name
        if special_day.discount_code_prefix:
            prefix = special_day.discount_code_prefix.upper()
        else:
            # Create prefix from event name
            prefix = ''.join(word[:4].upper() for word in special_day.name.split()[:2])
        
        # Add year
        code = f"{prefix}{year}"
        
        # Ensure uniqueness
        from discounts.models import Discount
        counter = 1
        original_code = code
        # Discount model uses 'discount_code' not 'code'
        while Discount.objects.filter(discount_code=code).exists():
            code = f"{original_code}{counter}"
            counter += 1
        
        return code
    
    @staticmethod
    def create_discount_for_special_day(special_day, year=None, created_by=None):
        """Create a discount code for a special day."""
        if year is None:
            year = timezone.now().year
        
        # Check if campaign already exists
        campaign = HolidayDiscountCampaign.objects.filter(
            special_day=special_day,
            year=year
        ).first()
        
        if campaign:
            return campaign.discount
        
        # Generate discount code
        code = HolidayDiscountService.generate_discount_code(special_day, year)
        
        # Calculate dates
        event_date = special_day.get_date_for_year(year)
        valid_from = event_date
        valid_until = event_date + timezone.timedelta(days=special_day.discount_valid_days)
        
        # Create discount
        from discounts.models import Discount
        discount = Discount.objects.create(
            code=code,
            percentage=special_day.discount_percentage or 10.00,
            valid_from=valid_from,
            valid_until=valid_until,
            is_active=True,
            description=f"Special {special_day.name} discount",
            created_by=created_by
        )
        
        # Create campaign
        campaign = HolidayDiscountCampaign.objects.create(
            special_day=special_day,
            discount=discount,
            year=year,
            auto_generated=special_day.auto_generate_discount,
            created_by=created_by
        )
        
        return discount
    
    @staticmethod
    def auto_generate_discounts_for_upcoming():
        """Auto-generate discounts for upcoming special days that have auto_generate_discount enabled."""
        today = timezone.now().date()
        generated = []
        
        # Get upcoming special days with auto-generate enabled
        special_days = SpecialDay.objects.filter(
            is_active=True,
            auto_generate_discount=True
        )
        
        for special_day in special_days:
            event_date = special_day.get_date_for_year()
            
            # If annual and passed this year, check next year
            if special_day.is_annual and event_date < today:
                event_date = special_day.get_date_for_year(today.year + 1)
            
            # Generate discount if within reminder period
            days_until = (event_date - today).days
            if days_until <= special_day.reminder_days_before:
                year = event_date.year
                
                # Check if already generated
                if not HolidayDiscountCampaign.objects.filter(
                    special_day=special_day,
                    year=year
                ).exists():
                    discount = HolidayDiscountService.create_discount_for_special_day(
                        special_day,
                        year=year
                    )
                    generated.append(discount)
        
        return generated


class HolidayNotificationService:
    """Service for sending notifications about holidays."""
    
    @staticmethod
    def notify_admins_of_upcoming_holidays():
        """Notify admins about upcoming holidays that need attention."""
        from notifications_system.services.core import NotificationService
        
        reminders = HolidayReminderService.get_pending_reminders()
        
        for reminder in reminders:
            special_day = reminder.special_day
            event_date = special_day.get_date_for_year()
            
            # Get admin users
            admins = User.objects.filter(
                role__in=['admin', 'superadmin'],
                is_active=True
            )
            
            message = (
                f"Upcoming Special Day: {special_day.name} on {event_date.strftime('%B %d, %Y')}\n\n"
                f"Don't forget to send a broadcast message to clients!"
            )
            
            if special_day.auto_generate_discount and not reminder.discount_created:
                message += "\n\nA discount code can be auto-generated for this event."
            
            for admin in admins:
                NotificationService.create_notification(
                    user=admin,
                    notification_type='holiday_reminder',
                    title=f"Special Day Reminder: {special_day.name}",
                    message=message,
                    metadata={
                        'reminder_id': reminder.id,
                        'special_day_id': special_day.id,
                        'event_date': str(event_date)
                    }
                )

