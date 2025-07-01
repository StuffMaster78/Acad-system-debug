from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from communications.models import (
    CommunicationMessage,
    FlaggedMessage,
    DisputeMessage,
    CommunicationNotification
)

User = get_user_model()


class NotificationService:
    """"
    Service class for handling notifications related to communication events.
    This class abstracts the logic for notifying users about new messages,
    flagged messages, sensitive uploads, and disputes.
    It provides methods to create notifications based on various triggers
    such as new messages, flagged content, and disputes.
    It also includes methods to notify admins about important events
    such as flagged messages and disputes.
    It ensures that notifications are created efficiently and correctly
    based on the context of the communication.
    """
    @staticmethod
    def notify_user_on_message(msg: CommunicationMessage):
        """
        Notify recipient of a new message if allowed.

        Args:
            msg (CommunicationMessage): The new message.
        """
        recipient = msg.recipient
        if not recipient or msg.is_hidden:
            return

        role = getattr(recipient.profile, "role", None)

        if role == "client" and "client" not in msg.visible_to_roles:
            return
        if role == "writer" and "writer" not in msg.visible_to_roles:
            return

        preview = msg.message[:100]
        if len(msg.message) > 100:
            preview += "..."

        CommunicationNotification.objects.create(
            recipient=recipient,
            message=msg,
            notification_text=f"New message: {preview}",
            is_read=False,
            created_at=timezone.now()
        )

    @staticmethod
    def notify_admin_on_flagged_message(flag: FlaggedMessage):
        """
        Notify all admins when a message is flagged.

        Args:
            flag (FlaggedMessage): The flagged message instance.
        """
        admins = User.objects.filter(is_staff=True)
        raw = flag.message.message or ""
        preview = raw[:100] + ("..." if len(raw) > 100 else "")

        notifications = [
            CommunicationNotification(
                recipient=admin,
                message=flag.message,
                notification_text=f"Flagged Message: {preview}",
                is_read=False,
                created_at=timezone.now()
            )
            for admin in admins
        ]
        CommunicationNotification.objects.bulk_create(notifications)

    @staticmethod
    def notify_admin_on_sensitive_upload(msg: CommunicationMessage):
        """
        Notify admins on file/image/link uploads from writers or clients.

        Args:
            msg (CommunicationMessage): The uploaded message.
        """
        sender_role = getattr(msg.sender.profile, "role", None)
        if sender_role not in {"client", "writer"}:
            return

        upload_label = {
            "file": "File Upload",
            "image": "Image Upload",
            "link": "Link Shared"
        }.get(msg.message_type, "Upload")

        raw = msg.message or ""
        preview = raw[:100] + ("..." if len(raw) > 100 else "")

        admins = User.objects.filter(is_staff=True)
        notifications = [
            CommunicationNotification(
                recipient=admin,
                message=msg,
                notification_text=(
                    f"{upload_label} requires approval: {preview}"
                ),
                is_read=False,
                created_at=timezone.now()
            )
            for admin in admins
        ]
        CommunicationNotification.objects.bulk_create(notifications)

    @staticmethod
    def notify_admin_on_dispute_created(dispute: DisputeMessage):
        """
        Notify admins about a new dispute.

        Args:
            dispute (DisputeMessage): The dispute created.
        """
        admins = User.objects.filter(is_staff=True)
        preview = dispute.content[:100]
        if len(dispute.content) > 100:
            preview += "..."

        text = (
            f"Dispute from {dispute.sender.username}: {preview}"
        )

        notifications = [
            CommunicationNotification(
                recipient=admin,
                message=dispute.message,
                notification_text=text,
                is_read=False,
                created_at=timezone.now()
            )
            for admin in admins
        ]
        CommunicationNotification.objects.bulk_create(notifications)

    @staticmethod
    def notify_admin_on_dispute_resolved(dispute: DisputeMessage):
        """
        Notify admins when a dispute is resolved.

        Args:
            dispute (DisputeMessage): The resolved dispute.
        """
        if dispute.status != "resolved":
            return

        admins = User.objects.filter(is_staff=True)
        text = (
            f"Dispute resolved for Order "
            f"{dispute.message.thread.order.id} - "
            f"{dispute.resolution_comment}"
        )

        notifications = [
            CommunicationNotification(
                recipient=admin,
                message=dispute.message,
                notification_text=text,
                is_read=False,
                created_at=timezone.now()
            )
            for admin in admins
        ]
        CommunicationNotification.objects.bulk_create(notifications)