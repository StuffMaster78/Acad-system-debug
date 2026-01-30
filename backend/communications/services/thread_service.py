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
        if order and getattr(order, "is_special", False):
            raise PermissionDenied("Special orders do not support threads.")

        # Class bundles are handled via ClassBundleCommunicationService
        # Skip this check if order is None (class bundle threads or general threads)
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
        
        if not website and order:
            # If we have an order, try to get website from it
            website = getattr(order, 'website', None)
        
        if not website:
            # For general threads (no order), try to get website from user
            if hasattr(created_by, 'website'):
                website = created_by.website
            elif hasattr(created_by, 'user_main_profile') and created_by.user_main_profile:
                website = getattr(created_by.user_main_profile, 'website', None)
        
        if not website:
            raise PermissionDenied("Website is required for thread creation.")
        
        # Determine sender_role and recipient_role from participants
        # Use created_by as the actual sender to ensure correct tab filtering
        sender_role = "client"  # Default
        recipient_role = "writer"  # Default
        
        if participants:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get all participants as User objects
            participant_users = []
            for p in participants:
                if isinstance(p, User):
                    participant_users.append(p)
                else:
                    participant_users.append(User.objects.get(id=p))
            
            # Get the actual sender (created_by) - this is who initiated the thread
            sender = created_by
            sender_role = getattr(sender, 'role', 'client')
            
            # Find the recipient (the other participant, not the sender)
            recipients = [p for p in participant_users if p.id != sender.id]
            
            if recipients:
                # Use the first recipient's role
                recipient = recipients[0]
                recipient_role = getattr(recipient, 'role', 'writer')
            elif len(participant_users) == 1:
                # Only one participant (the sender), determine recipient based on sender role
                if sender_role in ['admin', 'superadmin', 'support', 'editor']:
                    recipient_role = 'client'
                elif sender_role == 'client':
                    recipient_role = 'writer'
                elif sender_role == 'writer':
                    recipient_role = 'support'  # Writers typically message support
                else:
                    recipient_role = 'client'
        
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

    @staticmethod
    def create_special_order_thread(special_order, created_by, participants, thread_type="special", website=None):
        """
        Creates a communication thread for a special order.
        """
        if not special_order:
            raise PermissionDenied("Special order is required.")

        # Get website from special order if not provided
        if not website:
            website = getattr(special_order, "website", None)
        if not website:
            raise PermissionDenied("Website is required for thread creation.")

        # Determine sender_role and recipient_role from participants
        sender_role = "client"
        recipient_role = "writer"

        if participants:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            participant_users = []
            for p in participants:
                if isinstance(p, User):
                    participant_users.append(p)
                else:
                    participant_users.append(User.objects.get(id=p))

            sender = created_by
            sender_role = getattr(sender, "role", "client")

            recipients = [p for p in participant_users if p.id != sender.id]
            if recipients:
                recipient = recipients[0]
                recipient_role = getattr(recipient, "role", "writer")
            elif len(participant_users) == 1:
                if sender_role in ["admin", "superadmin", "support", "editor"]:
                    recipient_role = "client"
                elif sender_role == "client":
                    recipient_role = "writer"
                elif sender_role == "writer":
                    recipient_role = "support"
                else:
                    recipient_role = "client"

        thread = CommunicationThread.objects.create(
            special_order=special_order,
            website=website,
            thread_type=thread_type,
            sender_role=sender_role,
            recipient_role=recipient_role,
            is_active=True
        )

        thread.participants.set(participants)
        return thread