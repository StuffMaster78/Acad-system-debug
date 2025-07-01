from django.core.exceptions import PermissionDenied
from communications.models import CommunicationThread


class ThreadService:
    @staticmethod
    def create_thread(order, created_by, participants):
        """
        Creates a communication thread if allowed.

        Args:
            order (Order): The associated order.
            created_by (User): The initiator of the thread.
            participants (list): Users to include.

        Returns:
            CommunicationThread: The created thread.

        Raises:
            PermissionDenied: If thread creation is blocked.
        """
        if order.status == "archived":
            raise PermissionDenied("Cannot create thread on archived orders.")

        if getattr(order, "is_special", False):
            raise PermissionDenied("Special orders do not support threads.")

        if getattr(order, "is_class", False):
            raise PermissionDenied("Class orders do not support threads.")

        thread = CommunicationThread.objects.create(
            order=order,
            created_by=created_by,
            is_active=True
        )

        thread.participants.set(participants)
        return thread