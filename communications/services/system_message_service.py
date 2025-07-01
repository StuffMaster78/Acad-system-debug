# communications/services/system_message_service.py

from django.utils import timezone
from communications.models import CommunicationMessage, MessageType
from communications.models import CommunicationThread
from users.models import User
from communications.models import CommunicationLog

class SystemMessageService:
    SYSTEM_USER_USERNAME = "system"

    @classmethod
    def post(
        cls, *, thread: CommunicationThread, message: str,
        triggered_by: User = None, metadata: dict = None
    ) -> CommunicationMessage:
        """
        Create a system message in a thread.
        Does not send notifications or emails — just logs the message.
        """
        system_user = cls.get_system_user()

        message_obj = CommunicationMessage.objects.create(
            thread=thread,
            sender=system_user,
            message=message,
            message_type=MessageType.SYSTEM,
            sent_at=timezone.now(),
            metadata=metadata or {},
        )

        if triggered_by:
            CommunicationLog.objects.create(
                user=triggered_by,
                order=thread.order,
                action="system_message",
                details=f"{triggered_by.get_display_name()} triggered system message: '{message}'"
            )

        return message_obj

    @classmethod
    def get_system_user(cls):
        return User.objects.get_or_create(
            username=cls.SYSTEM_USER_USERNAME,
            defaults=dict(email="system@yourapp.com", is_active=False)
        )[0]