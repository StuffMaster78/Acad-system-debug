from django.core.exceptions import PermissionDenied
from communications.models import CommunicationThread


class ThreadService:
    @staticmethod
    def create_thread(order, created_by, participants, thread_type="order", website=None):
        """
        Creates a communication thread if allowed.

        Args:
            order (Order): The associated order.
            created_by (User): The initiator of the thread.
            participants (list): Users to include.
            thread_type (str): Type of thread (default: "order").
            website (Website, optional): Website for the thread (will be derived from order if not provided).

        Returns:
            CommunicationThread: The created thread.

        Raises:
            PermissionDenied: If thread creation is blocked.
        """
        if order.status == "archived":
            raise PermissionDenied("Cannot create thread on archived orders.")

        # Note: Special orders and class bundles use GenericRelation
        # and are handled separately via their own thread creation methods
        if getattr(order, "is_special", False):
            raise PermissionDenied("Special orders do not support threads.")

        # Class bundles are handled via ClassBundleCommunicationService
        # Skip this check if order is None (class bundle threads)
        if order and getattr(order, "is_class", False):
            raise PermissionDenied("Class orders do not support threads.")

        # Get website from order if not provided
        if not website:
            website = getattr(order, 'website', None)
            if not website:
                # Try to get website from order's website_id
                website_id = getattr(order, 'website_id', None)
                if website_id:
                    from websites.models import Website
                    try:
                        website = Website.objects.get(id=website_id)
                    except Website.DoesNotExist:
                        pass
        
        if not website:
            raise PermissionDenied("Website is required for thread creation.")
        
        # Determine sender_role and recipient_role from participants
        # For order threads, typically client and writer
        sender_role = "client"  # Default
        recipient_role = "writer"  # Default
        
        if participants:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            first_participant = participants[0] if isinstance(participants[0], User) else User.objects.get(id=participants[0])
            if hasattr(first_participant, 'role'):
                sender_role = first_participant.role or "client"
            if len(participants) > 1:
                second_participant = participants[1] if isinstance(participants[1], User) else User.objects.get(id=participants[1])
                if hasattr(second_participant, 'role'):
                    recipient_role = second_participant.role or "writer"
        
        thread = CommunicationThread.objects.create(
            order=order,
            website=website,
            thread_type=thread_type,
            sender_role=sender_role,
            recipient_role=recipient_role,
            is_active=True
        )

        thread.participants.set(participants)
        return thread