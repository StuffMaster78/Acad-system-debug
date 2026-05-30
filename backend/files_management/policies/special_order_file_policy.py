from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class SpecialOrderFilePolicy(BaseFilePolicy):
    """
    Access policy for files attached to special order objects.

    Special orders involve sensitive deliverables, milestone files,
    portal credentials, and screenshots. The policy mirrors the order
    policy for client/writer visibility but adds stricter defaults for
    credential and screenshot categories (STAFF_ONLY).

    Sensitive files (is_sensitive=True) are gated by FileAccessService
    before this policy is evaluated — so a sensitive attachment only
    reaches here if the user is staff or holds an explicit grant.
    """

    domain_key = "special_orders"

    SPECIAL_ORDER_APP_LABELS = {
        "special_orders",
        "specialorders",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        return (
            attachment.content_type.app_label.lower()
            in self.SPECIAL_ORDER_APP_LABELS
        )

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
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

        if self._is_client(user=user, obj=obj):
            return attachment.visibility in {
                FileVisibility.CLIENT_AND_STAFF,
                FileVisibility.CLIENT_WRITER_STAFF,
                FileVisibility.ORDER_PARTICIPANTS,
            }

        if self._is_writer(user=user, obj=obj):
            return attachment.visibility in {
                FileVisibility.WRITER_AND_STAFF,
                FileVisibility.CLIENT_WRITER_STAFF,
                FileVisibility.ORDER_PARTICIPANTS,
            }

        return False

    def can_replace(self, *, user, attachment: FileAttachment) -> bool:
        if self.is_staff_like(user=user):
            return self.is_same_website(user=user, attachment=attachment)
        return self.is_uploader(user=user, attachment=attachment)

    def can_request_deletion(
        self, *, user, attachment: FileAttachment
    ) -> bool:
        if not self.is_same_website(user=user, attachment=attachment):
            return False
        return self.is_staff_like(user=user) or self.is_uploader(
            user=user, attachment=attachment
        )

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    @staticmethod
    def _is_client(*, user, obj) -> bool:
        user_id = getattr(user, "id", None)
        for attr in ("client_id", "user_id", "customer_id"):
            if getattr(obj, attr, None) == user_id:
                return True
        client = getattr(obj, "client", None)
        if getattr(client, "user_id", None) == user_id:
            return True
        return getattr(client, "id", None) == user_id

    @staticmethod
    def _is_writer(*, user, obj) -> bool:
        user_id = getattr(user, "id", None)
        for attr in ("writer_id", "assigned_writer_id"):
            if getattr(obj, attr, None) == user_id:
                return True
        writer = getattr(obj, "writer", None)
        if getattr(writer, "user_id", None) == user_id:
            return True
        return getattr(writer, "id", None) == user_id
