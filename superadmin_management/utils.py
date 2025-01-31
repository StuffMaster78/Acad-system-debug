from django.contrib.auth import get_user_model
from django.utils.timezone import now
from notifications_system.models import Notification  # Import from your Notifications App

User = get_user_model()

class SuperadminNotifier:
    """Handles sending notifications to Superadmins via the Notifications App."""

    @staticmethod
    def notify_superadmins(title, message, category="general"):
        """
        Sends a notification to all Superadmins.

        :param title: Notification title
        :param message: Notification body
        :param category: Type of notification (e.g., user, security, financial, order, dispute)
        """
        superadmins = User.objects.filter(role="superadmin")
        for superadmin in superadmins:
            Notification(
                recipient=superadmin,
                title=title,
                message=message,
                category=category,
                timestamp=now(),
            )
