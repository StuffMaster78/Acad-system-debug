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
        # This is important for filtering threads correctly
        sender_role = "client"  # Default
        recipient_role = "writer"  # Default
        
        if participants:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get all participant roles
            participant_roles = []
            for p in participants:
                if isinstance(p, User):
                    participant = p
                else:
                    participant = User.objects.get(id=p)
                
                role = getattr(participant, 'role', None)
                if role:
                    participant_roles.append(role)
            
            # Set sender_role and recipient_role based on participant roles
            # Priority: admin/superadmin/support/editor > client > writer
            if len(participant_roles) >= 2:
                # Sort roles by priority for consistent assignment
                role_priority = {'superadmin': 0, 'admin': 1, 'support': 2, 'editor': 3, 'client': 4, 'writer': 5}
                sorted_roles = sorted(participant_roles, key=lambda r: role_priority.get(r, 99))
                sender_role = sorted_roles[0]
                recipient_role = sorted_roles[1]
            elif len(participant_roles) == 1:
                sender_role = participant_roles[0]
                # If only one participant, set recipient_role to the other expected role
                if sender_role in ['admin', 'superadmin', 'support', 'editor']:
                    recipient_role = 'client'
                elif sender_role == 'client':
                    recipient_role = 'writer'
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