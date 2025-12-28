"""
Service for managing review reminders.
"""
from django.utils import timezone
from datetime import timedelta
from orders.models import ReviewReminder, Order
from websites.models import ExternalReviewLink


class ReviewReminderService:
    """Service for managing review reminders."""
    
    @staticmethod
    def create_reminder_on_order_completion(order: Order):
        """Create a review reminder when an order is completed."""
        if not order.client or order.client.role != 'client':
            return None
        
        return ReviewReminder.create_for_order(order)
    
    @staticmethod
    def get_due_reminders():
        """Get reminders that are due to be sent."""
        return ReviewReminder.objects.filter(
            is_completed=False,
            next_reminder_at__lte=timezone.now()
        ).select_related('order', 'client', 'writer', 'order__website')
    
    @staticmethod
    def get_external_review_links(website, review_type='general'):
        """Get active external review links for a website."""
        return ExternalReviewLink.objects.filter(
            website=website,
            is_active=True,
            review_type__in=[review_type, 'general']
        ).order_by('display_order')
    
    @staticmethod
    def send_reminder(reminder: ReviewReminder):
        """Send a review reminder notification with external review links."""
        from communications.services.notification_service import NotificationService
        from notifications_system.services.core import NotificationService as NotifService
        
        reminder.send_reminder()
        
        # Get external review links for the website
        website = reminder.order.website
        order_links = ReviewReminderService.get_external_review_links(website, 'order')
        writer_links = ReviewReminderService.get_external_review_links(website, 'writer')
        website_links = ReviewReminderService.get_external_review_links(website, 'website')
        
        # Build message with review links
        message_parts = [
            f"Please review and rate your writer for order #{reminder.order.id}."
        ]
        
        if order_links.exists() or writer_links.exists() or website_links.exists():
            message_parts.append("\n\nYou can also leave reviews on external sites:")
            
            if order_links.exists():
                message_parts.append("\nOrder Reviews:")
                for link in order_links:
                    message_parts.append(f"  • {link.review_site_name}: {link.review_url}")
            
            if writer_links.exists():
                message_parts.append("\nWriter Reviews:")
                for link in writer_links:
                    message_parts.append(f"  • {link.review_site_name}: {link.review_url}")
            
            if website_links.exists():
                message_parts.append("\nWebsite Reviews:")
                for link in website_links:
                    message_parts.append(f"  • {link.review_site_name}: {link.review_url}")
        
        message = "\n".join(message_parts)
        
        # Send notification with metadata including review links
        try:
            NotifService.send_notification(
                user=reminder.client,
                notification_type="review_reminder",
                title="Review Reminder",
                message=message,
                metadata={
                    "order_id": reminder.order.id,
                    "external_review_links": {
                        "order": [{"name": link.review_site_name, "url": link.review_url} for link in order_links],
                        "writer": [{"name": link.review_site_name, "url": link.review_url} for link in writer_links],
                        "website": [{"name": link.review_site_name, "url": link.review_url} for link in website_links],
                    }
                }
            )
        except Exception:
            # Fallback to basic notification if enhanced service fails
            NotificationService.send_notification(
                user=reminder.client,
                title="Review Reminder",
                message=message,
                notification_type="reminder"
            )
        
        return reminder

