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
        enforce_visibility: bool=True,
        attachment_file=None
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
        # Auto-add sender to participants if they have order access but aren't a participant yet
        if sender not in thread.participants.all():
            order = getattr(thread, "order", None)
            if order:
                role = getattr(sender, "role", None)
                # Check if user has access to the order
                has_order_access = (
                    order.client == sender or
                    order.assigned_writer == sender or
                    role in {"admin", "superadmin", "editor", "support"}
                )
                if has_order_access:
                    thread.participants.add(sender)
                else:
                    raise ValueError("You don't have access to this order. Please contact support if you believe this is an error.")
            else:
                raise ValueError("You are not a participant in this conversation. Please contact support if you need access.")
        
        # Enforce order restrictions, including special, archived, etc.
        CommunicationGuardService.assert_can_send_message(sender, thread)

        if not thread.is_active and not thread.admin_override:
            raise ValueError("Messaging is disabled for this conversation. Please contact support if you need to send a message.")

        if not message or not message.strip():
            raise ValueError("Please enter a message or attach a file.")

        if reply_to and reply_to.thread != thread:
            raise ValueError("Replied-to message must belong to the same thread.")

        if reply_to and not MessageService.can_reply(sender, reply_to):
            raise PermissionError("You are not allowed to reply to this message.")

        recipient_role = getattr(recipient, "role", None)
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
            visible_to_roles=sorted(list(set([sender_role, recipient_role]))),  # Ensure unique and sorted to avoid constraint violations
            sent_at=timezone.now(),
            attachment=attachment_file
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

        # Log it - use shorter action name to fit max_length=20
        CommunicationLog.objects.create(
            user=sender,
            order=thread.order,
            action="sent",  # Use existing action choice
            details=sanitized_message[:200]
        )

        # Update thread's recipient_role based on actual message recipient
        # This ensures threads appear in the correct tabs based on who messages are sent TO
        if thread.recipient_role != recipient_role:
            thread.recipient_role = recipient_role
            thread.save(update_fields=['recipient_role'])
        
        # Also update sender_role if different (for consistency)
        if thread.sender_role != sender_role:
            thread.sender_role = sender_role
            thread.save(update_fields=['sender_role'])

        # Log to ActivityLog for activity page (async to avoid blocking message creation)
        try:
            from activity.utils.logger_safe import safe_log_activity
            order = getattr(thread, 'order', None)
            website = getattr(order, 'website', None) if order else getattr(thread, 'website', None)
            
            if website:
                # Determine description based on context (will be prefixed with "You" in serializer)
                recipient_role = getattr(recipient, 'role', None) if recipient else None
                if order:
                    if recipient_role == 'client':
                        description = f"sent a message to client #{recipient.id} about order #{order.id}"
                    elif recipient_role == 'writer':
                        description = f"sent a message to writer #{recipient.id} about order #{order.id}"
                    else:
                        description = f"sent a message about order #{order.id}"
                else:
                    if recipient_role == 'client':
                        description = f"sent a message to client #{recipient.id}"
                    elif recipient_role == 'writer':
                        description = f"sent a message to writer #{recipient.id}"
                    else:
                        description = f"sent a message to {recipient.email if recipient else 'recipient'}"
                
                # Use safe_log_activity which tries sync first, falls back to async
                # This prevents blocking the request if logging fails
                safe_log_activity(
                    user=sender,
                    website=website,
                    action_type="COMMUNICATION",
                    description=description,
                    metadata={
                        "message_id": comm_msg.id,
                        "thread_id": thread.id,
                        "order_id": order.id if order else None,
                        "recipient_id": recipient.id if recipient else None,
                        "message_type": inferred_type,
                    },
                    triggered_by=sender,
                )
        except Exception as e:
            # Don't break message creation if activity logging fails
            import logging
            logging.getLogger("activity").warning(f"Failed to log message activity: {e}")

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
        
        Visibility Rules (Matchmaking Platform):
        - Admin/Superadmin: See ALL messages (all communications)
        - Support: See messages where client sends to support (all support users can read)
        - Editor: See messages where client sends to editor (all editors can read)
        - Admin: See messages where client sends to admin (all admins can read)
        - Client: See messages where they are sender/recipient OR writer sends to them (only that specific client)
        - Writer: See messages where they are sender/recipient OR client sends to them (only that specific writer)

        Args:
            user (User): Requesting user.
            thread (CommunicationThread): The thread in question.

        Returns:
            QuerySet: Filtered messages.
        """
        role = getattr(user, "role", None)

        if role is None:
            return CommunicationMessage.objects.none()

        from django.db.models import Q
    
        # Admin/Superadmin: See ALL messages (all communications)
        if role in {"admin", "superadmin"}:
            return thread.messages.filter(is_deleted=False).order_by("sent_at")

        # Support: See messages where client sends to support (all support users can read)
        # Also see messages where they are sender/recipient
        if role == "support":
            return thread.messages.filter(
                is_deleted=False
            ).filter(
                Q(sender=user) | 
                Q(recipient=user) |
                (Q(sender_role="client") & Q(recipient_role="support"))
            ).order_by("sent_at")

        # Editor: See messages where client sends to editor (all editors can read)
        # Also see messages where they are sender/recipient
        if role == "editor":
            return thread.messages.filter(
                is_deleted=False
            ).filter(
                Q(sender=user) | 
                Q(recipient=user) |
                (Q(sender_role="client") & Q(recipient_role="editor"))
            ).order_by("sent_at")

        # Admin: See messages where client sends to admin (all admins can read)
        # Also see messages where they are sender/recipient
        # Note: This is for regular admin role (not superadmin)
        if role == "admin":
            return thread.messages.filter(
                is_deleted=False
            ).filter(
                Q(sender=user) | 
                Q(recipient=user) |
                (Q(sender_role="client") & Q(recipient_role__in=["admin", "superadmin"]))
            ).order_by("sent_at")

        # Client: See messages where they are sender/recipient OR writer sends to them (only that specific client)
        if role == "client":
            return thread.messages.filter(
                is_deleted=False
            ).filter(
                Q(sender=user) | 
                Q(recipient=user) |
                (Q(sender_role="writer") & Q(recipient=user))
            ).order_by("sent_at")

        # Writer: See messages where they are sender/recipient OR client sends to them (only that specific writer)
        if role == "writer":
            return thread.messages.filter(
                is_deleted=False
            ).filter(
                Q(sender=user) | 
                Q(recipient=user) |
                (Q(sender_role="client") & Q(recipient=user))
            ).order_by("sent_at")

        # Default: only messages where user is sender or recipient
        return thread.messages.filter(
            is_deleted=False
        ).filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by("sent_at")
    

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
        role = getattr(user, "role", None)
        return role in ["admin", "superadmin"]
    

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
        role = getattr(user, "role", None)
        return role in ["admin", "superadmin"]

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
        role = getattr(user, "role", None)

        if role not in allowed_roles:
            raise PermissionError("User is not authorized to join this thread.")

        thread.participants.add(user)


    @staticmethod
    def can_reply(user, message_obj: CommunicationMessage) -> bool:
        """
        Determines whether the user can reply to a given message.
        Allows all users with access to the order to reply.

        Args:
            user (User): The user attempting to reply.
            message_obj (CommunicationMessage): The message being replied to.

        Returns:
            bool: True if the user can reply, False otherwise.
        """
        role = getattr(user, "role", None) or getattr(user, "role", None)

        if message_obj.is_deleted:
            return False

        thread = message_obj.thread
        order = getattr(thread, "order", None)
        
        # Check if user has access to the order
        has_order_access = False
        
        # User is a participant
        if user in thread.participants.all():
            has_order_access = True
        # Check order access
        elif order:
            # Client who placed the order
            if order.client == user:
                has_order_access = True
            # Writer assigned to the order
            elif order.assigned_writer == user:
                has_order_access = True
            # Staff roles have access
            elif role in {"admin", "superadmin", "editor", "support"}:
                has_order_access = True

        if not has_order_access:
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