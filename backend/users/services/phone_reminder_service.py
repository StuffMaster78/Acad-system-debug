"""
Phone Number Reminder Service
Reminds clients to update their phone number for order coordination and urgent contact.
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from users.models import UserProfile
from client_management.models import ClientProfile

logger = logging.getLogger(__name__)


class PhoneReminderService:
    """
    Service for checking and reminding clients about phone number updates.
    """
    
    def __init__(self, user):
        self.user = user
    
    def has_phone_number(self) -> bool:
        """
        Check if user has a phone number in either UserProfile or ClientProfile.
        
        Returns:
            True if user has a phone number, False otherwise
        """
        # Check UserProfile
        try:
            profile = self.user.user_main_profile
            if profile and profile.phone_number:
                return True
        except UserProfile.DoesNotExist:
            pass
        
        # Check ClientProfile (if user is a client)
        if self.user.role in ['client', 'customer']:
            try:
                client_profile = self.user.client_profile
                if client_profile and client_profile.phone_number:
                    return True
            except ClientProfile.DoesNotExist:
                pass
        
        return False
    
    def get_phone_number(self) -> Optional[str]:
        """
        Get the user's phone number from UserProfile or ClientProfile.
        
        Returns:
            Phone number string or None
        """
        # Check UserProfile first
        try:
            profile = self.user.user_main_profile
            if profile and profile.phone_number:
                return str(profile.phone_number)
        except UserProfile.DoesNotExist:
            pass
        
        # Check ClientProfile (if user is a client)
        if self.user.role in ['client', 'customer']:
            try:
                client_profile = self.user.client_profile
                if client_profile and client_profile.phone_number:
                    return client_profile.phone_number
            except ClientProfile.DoesNotExist:
                pass
        
        return None
    
    def needs_phone_reminder(self) -> bool:
        """
        Check if user needs a phone number reminder.
        Only clients need reminders.
        
        Returns:
            True if reminder is needed, False otherwise
        """
        if self.user.role not in ['client', 'customer']:
            return False
        
        return not self.has_phone_number()
    
    def get_reminder_info(self) -> Dict[str, Any]:
        """
        Get phone number reminder information for the user.
        
        Returns:
            Dict with reminder information
        """
        has_phone = self.has_phone_number()
        phone_number = self.get_phone_number() if has_phone else None
        
        return {
            'needs_reminder': self.needs_phone_reminder(),
            'has_phone_number': has_phone,
            'phone_number': phone_number,
            'message': (
                "Please update your phone number to help us coordinate order fulfillment "
                "and contact you urgently when needed."
            ) if not has_phone else None,
            'reasons': [
                "Order fulfillment coordination",
                "Urgent contact when needed",
                "Better communication during order process"
            ] if not has_phone else [],
        }
    
    def should_show_reminder_in_order_context(self, order=None) -> bool:
        """
        Check if reminder should be shown in order context.
        Show reminder if:
        - User is a client
        - No phone number
        - Order exists and is in active status
        
        Args:
            order: Optional Order instance
        
        Returns:
            True if reminder should be shown
        """
        if not self.needs_phone_reminder():
            return False
        
        # If order is provided, check if it's in an active status
        if order:
            active_statuses = [
                'pending', 'in_progress', 'submitted', 'reviewed', 
                'rated', 'revision_requested', 'on_revision', 'revised'
            ]
            if order.status not in active_statuses:
                return False
        
        return True
    
    @staticmethod
    def send_reminder_notification(user, website=None, order=None):
        """
        Send a reminder notification to user about updating phone number.
        
        Args:
            user: User to send reminder to
            website: Website context
            order: Optional Order instance for context
        """
        if not website:
            from websites.utils import get_current_website
            website = get_current_website()
            if not website:
                from websites.models import Website
                website = Website.objects.filter(is_active=True).first()
        
        if not website:
            logger.warning(f"No website context for phone reminder for user {user.id}")
            return
        
        service = PhoneReminderService(user)
        if not service.needs_phone_reminder():
            return  # No reminder needed
        
        # Check if reminder should be shown in order context
        if order and not service.should_show_reminder_in_order_context(order):
            return
        
        try:
            from notifications_system.services.core import NotificationService
            NotificationService.send_notification(
                user=user,
                event='profile.phone_reminder',
                payload={
                    'message': (
                        'Please update your phone number to help us coordinate '
                        'order fulfillment and contact you urgently when needed.'
                    ),
                    'action_url': '/account/settings',
                    'action_text': 'Update Phone Number',
                    'order_id': order.id if order else None,
                },
                website=website,
                category='profile',
                priority='medium',
                is_critical=False,
            )
        except Exception as e:
            logger.warning(f"Failed to send phone reminder notification: {e}")

