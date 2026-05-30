from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class ClassFilePolicy(BaseFilePolicy):
    """
    Access policy for class, course, bundle, and lesson files.
    """

    domain_key = "classes"

    CLASS_APP_LABELS = {
        "classes",
        "class_management",
        "courses",
        "bundles",
        "learning",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether this attachment belongs to class workflows.
        """

        return attachment.content_type.app_label.lower() in self.CLASS_APP_LABELS

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can view class files.

        Visibility flags are evaluated before the enrolled/owner fallback
        so STAFF_ONLY and WRITER_AND_STAFF files are not visible to clients.
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

        if attachment.visibility in {
            FileVisibility.PUBLIC,
            FileVisibility.CMS_PUBLIC,
        }:
            return True

        obj = attachment.content_object
        if obj is None:
            return False

        is_client = self._is_enrolled_or_owner(user=user, obj=obj)
        is_writer = self._is_class_writer(user=user, obj=obj)

        if attachment.visibility == FileVisibility.WRITER_AND_STAFF:
            return is_writer

        if attachment.visibility == FileVisibility.CLIENT_AND_STAFF:
            return is_client

        # ORDER_PARTICIPANTS and CLIENT_WRITER_STAFF — both parties
        if attachment.visibility in {
            FileVisibility.ORDER_PARTICIPANTS,
            FileVisibility.CLIENT_WRITER_STAFF,
        }:
            return is_client or is_writer

        return is_client

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow staff or uploaders to request deletion.
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
    def _is_enrolled_or_owner(*, user, obj) -> bool:
        user_id = getattr(user, "id", None)

        for attr_name in ("client_id", "owner_id", "user_id"):
            if getattr(obj, attr_name, None) == user_id:
                return True

        client = getattr(obj, "client", None)
        if getattr(client, "user_id", None) == user_id:
            return True
        if getattr(client, "id", None) == user_id:
            return True

        enrollments = getattr(obj, "enrollments", None)
        if enrollments is None:
            return False

        try:
            return enrollments.filter(user_id=user_id).exists()
        except AttributeError:
            return False

    @staticmethod
    def _is_class_writer(*, user, obj) -> bool:
        user_id = getattr(user, "id", None)

        for attr_name in ("assigned_writer_id", "writer_id"):
            if getattr(obj, attr_name, None) == user_id:
                return True

        writer = getattr(obj, "assigned_writer", None) or getattr(
            obj, "writer", None
        )
        if getattr(writer, "user_id", None) == user_id:
            return True
        return getattr(writer, "id", None) == user_id