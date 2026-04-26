from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class SupportFilePolicy(BaseFilePolicy):
    """
    Access policy for support ticket and dispute files.
    """

    domain_key = "support"

    SUPPORT_APP_LABELS = {
        "support",
        "support_tickets",
        "tickets",
        "disputes",
        "refunds",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether this attachment belongs to support workflows.
        """

        return (
            attachment.content_type.app_label.lower()
            in self.SUPPORT_APP_LABELS
        )

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow staff and ticket participants to view support files.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        if attachment.visibility in {
            FileVisibility.STAFF_ONLY,
            FileVisibility.INTERNAL_ONLY,
        }:
            return False

        obj = attachment.content_object

        if obj is None:
            return False

        return self._is_ticket_participant(user=user, obj=obj)

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow uploaders and staff to request deletion.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        return self.is_staff_like(user=user) or self.is_uploader(
            user=user,
            attachment=attachment,
        )

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow only staff direct deletion.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    @staticmethod
    def _is_ticket_participant(*, user, obj) -> bool:
        """
        Return whether the user belongs to the support object.
        """

        user_id = getattr(user, "id", None)

        for attr_name in (
            "created_by_id",
            "submitted_by_id",
            "client_id",
            "writer_id",
            "user_id",
        ):
            if getattr(obj, attr_name, None) == user_id:
                return True

        return False