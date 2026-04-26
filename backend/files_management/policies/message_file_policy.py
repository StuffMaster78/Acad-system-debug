from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class MessageFilePolicy(BaseFilePolicy):
    """
    Access policy for message attachments.

    Message attachments are sensitive because users may try to bypass
    platform communication rules by sharing contacts, IDs, payment
    details, or personal documents through files.

    Backend policy controls access and deletion. Frontend and future
    scanning layers should help detect personal data risks.
    """

    domain_key = "messages"

    MESSAGE_MODEL_NAMES = {
        "message",
        "conversationmessage",
        "chatmessage",
        "threadmessage",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether the attachment belongs to a message object.
        """

        model_name = attachment.content_type.model.lower()
        app_label = attachment.content_type.app_label.lower()

        return (
            app_label in {"messages", "messaging", "chats"}
            or model_name in self.MESSAGE_MODEL_NAMES
        )

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow conversation participants and staff to view attachments.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        if attachment.visibility != FileVisibility.CONVERSATION_PARTICIPANTS:
            return self.is_uploader(user=user, attachment=attachment)

        message_obj = attachment.content_object

        if message_obj is None:
            return False

        return self._is_conversation_participant(
            user=user,
            message_obj=message_obj,
        )

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow uploaders or participants to request deletion.

        Direct deletion remains staff-only to preserve audit evidence.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        if self.is_uploader(user=user, attachment=attachment):
            return True

        message_obj = attachment.content_object

        if message_obj is None:
            return False

        return self._is_conversation_participant(
            user=user,
            message_obj=message_obj,
        )

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Prevent clients and writers from deleting message attachments.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    @staticmethod
    def _is_conversation_participant(*, user, message_obj) -> bool:
        """
        Return whether the user belongs to the message conversation.

        This supports several common message model shapes while keeping
        the file app decoupled from one messaging implementation.
        """

        user_id = getattr(user, "id", None)

        for attr_name in ("sender_id", "recipient_id", "user_id"):
            if getattr(message_obj, attr_name, None) == user_id:
                return True

        conversation = getattr(message_obj, "conversation", None)
        thread = getattr(message_obj, "thread", None)
        parent = conversation or thread

        if parent is None:
            return False

        for attr_name in ("client_id", "writer_id", "user_id"):
            if getattr(parent, attr_name, None) == user_id:
                return True

        participants = getattr(parent, "participants", None)

        if participants is None:
            return False

        try:
            return participants.filter(id=user_id).exists()
        except AttributeError:
            return False