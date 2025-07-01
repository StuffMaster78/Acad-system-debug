import re
from django.utils import timezone
from django.db import transaction
from communications.models import (
    CommunicationMessage, FlaggedMessage,
    CommunicationThread, CommunicationLog
)
from users.models import UserProfile
from communications.rules import get_visibility_flags
from communications.utils import contains_restricted_content
from communications.services.notification_service import (
    NotificationService
)
from communications.utils import extract_first_link
from django.core.exceptions import PermissionDenied
from communications.services.communication_guard import (
    CommunicationGuardService
)

class MessageService:
    """
    Service class for handling message-related operations,
    including creation, visibility rules, and content sanitization.
    This class abstracts the logic for creating messages with visibility rules
    based on user roles, and it also handles the sanitization of message content
    to ensure compliance with content policies.
    """
    @staticmethod
    @transaction.atomic
    def create_message(
        thread: CommunicationThread,
        sender,
        recipient,
        sender_role: str,
        message: str,
        link: str = None,
        domain: str = None,
        message_type: str = "text",
        *,
        reply_to: CommunicationMessage = None,
        enforce_visibility: bool=True
    ) -> CommunicationMessage:
        """
        Creates a message in a thread, applying sanitization, visibility rules,
        and admin flagging if restricted content is found.

        Args:
            thread (CommunicationThread): The thread to post to.
            sender (User): Sender user object.
            recipient (User): Recipient user object.
            sender_role (str): Role of the sender.
            message (str): Message content.
            reply_to (CommunicationMessage, optional): Message being replied to.
            enforce_visibility (bool): Whether to apply visibility filtering.

        Returns:
            CommunicationMessage: The newly created message.
        Raises:
            ValueError: If messaging is disabled or message is empty.
        """
        if sender not in thread.participants.all():
            raise ValueError("Sender is not a participant of this thread.")
        
        # Enforce order restrictions, including special, archived, etc.
        CommunicationGuardService.assert_can_send_message(sender, thread)

        if not thread.is_active and not thread.admin_override:
            raise ValueError("Messaging is disabled for this thread.")

        if not message or not message.strip():
            raise ValueError("Empty messages are not allowed.")

        if reply_to and reply_to.thread != thread:
            raise ValueError("Replied-to message must belong to the same thread.")

        if reply_to and not MessageService.can_reply(sender, reply_to):
            raise PermissionError("You are not allowed to reply to this message.")

        recipient_role = getattr(recipient.profile, "role", None)
        if recipient_role is None:
            raise ValueError("Recipient must have a valid profile with role.")

        visible_to_client, visible_to_writer = get_visibility_flags(
            sender_role, recipient_role
        )

        # Sanitize and flag
        sanitized_message, flagged_by_content = contains_restricted_content(message)

        # Link logic
        link_url = extract_first_link(sanitized_message)
        contains_link = bool(link_url)
        link_domain = link_url.split("/")[2] if link_url else None

        # Determine type
        inferred_type = "link" if contains_link else message_type
        if inferred_type not in {"text", "file", "image", "link"}:
            raise ValueError("Invalid message type.")
        
        # Flag if risky
        flagged_by_type = inferred_type in {"file", "image", "link"}
        is_flagged = flagged_by_content or contains_link or flagged_by_type
        is_hidden = is_flagged

        # Compose message object (Final Object)
        comm_msg = CommunicationMessage.objects.create(
            thread=thread,
            sender=sender,
            recipient=recipient,
            sender_role=sender_role,
            message=sanitized_message.strip(),
            message_type=inferred_type,
            is_flagged=is_flagged,
            is_hidden=is_hidden,
            contains_link=contains_link,
            link_url=link_url,
            link_domain=link_domain or domain,
            is_link_approved=False if inferred_type == "link" else True,
            reply_to=reply_to,
            visible_to_roles=[sender_role, recipient_role],
            sent_at=timezone.now()
        )

        # Admin gets notified on flagged messages
        if is_flagged:
            flag= FlaggedMessage.objects.create(
                message=comm_msg,
                flagged_reason="Contains restricted content"
            )
            NotificationService.notify_admin_on_flagged_message(flag)

        # Admins also get pinged for uploads (file, image, link)
        if message_type in ["file", "image", "link"]:
            NotificationService.notify_admin_on_sensitive_upload(comm_msg)

        # Notify recipient normally
        NotificationService.notify_user_on_message(comm_msg)

        # Log it
        CommunicationLog.objects.create(
            user=sender,
            order=thread.order,
            action="communication_message_created",
            details=sanitized_message[:200]
        )

        # Spam control
        recent_count = CommunicationMessage.objects.filter(
            sender=sender,
            thread=thread,
            sent_at__gte=timezone.now() - timezone.timedelta(seconds=10)
        ).count()
        if recent_count > 5:
            raise ValueError("Too many messages. Please slow down.")

        return comm_msg


    @staticmethod
    def get_visible_messages(user, thread: CommunicationThread):
        """
        Fetch messages in a thread visible to the requesting user.

        Args:
            user (User): Requesting user.
            thread (CommunicationThread): The thread in question.

        Returns:
            QuerySet: Filtered messages.
        """
        role = getattr(user.profile, "role", None)

        if role is None:
            return CommunicationMessage.objects.none()

    
        if role in {"admin", "superadmin", "support", "editor"}:
            return thread.messages.filter(is_deleted=False)

        return thread.messages.filter(
            is_deleted=False,
            visible_to_roles__contains=[role]
        )
    

    @staticmethod
    def can_edit(
        user, message_obj: CommunicationMessage
    ) -> bool:
        """
        Check if a user has permission to edit a message.

        Args:
            user (User): User requesting edit access.
            message_obj (CommunicationMessage): Message to edit.

        Returns:
            bool: True if user can edit, False otherwise.
        """
        return user.profile.role in ["admin", "superadmin"]
    

    @staticmethod
    def can_delete(user, message_obj: CommunicationMessage) -> bool:
        """ 
        Check if a user has permission to delete a message.
        Args:
            user (User): User requesting delete access.
            message_obj (CommunicationMessage): Message to delete.
        Returns:
            bool: True if user can delete, False otherwise.
        """
        return user.profile.role in ["admin", "superadmin"]

    @staticmethod
    def join_thread(user, thread: CommunicationThread) -> None:
        """
        Allows privileged users (admin, superadmin, support) to join a thread.

        Args:
            user (User): The user joining the thread.
            thread (CommunicationThread): The thread to join.

        Raises:
            PermissionError: If the user's role is not allowed.
        """
        allowed_roles = {"admin", "superadmin", "support"}
        role = getattr(user.profile, "role", None)

        if role not in allowed_roles:
            raise PermissionError("User is not authorized to join this thread.")

        thread.participants.add(user)


    @staticmethod
    def can_reply(user, message_obj: CommunicationMessage) -> bool:
        """
        Determines whether the user can reply to a given message.

        Args:
            user (User): The user attempting to reply.
            message_obj (CommunicationMessage): The message being replied to.

        Returns:
            bool: True if the user can reply, False otherwise.
        """
        role = getattr(user.profile, "role", None)

        if message_obj.is_deleted:
            return False

        # Message must be in a thread the user is part of
        if user not in message_obj.thread.participants.all():
            return False

        # Visibility rules
        if role == "client" and "client" not in message_obj.visible_to_roles:
            return False
        if role == "writer" and "writer" not in message_obj.visible_to_roles:
            return False

        # Admins/support can always reply to anything
        if role in {"admin", "superadmin", "support"}:
            return True

        return True