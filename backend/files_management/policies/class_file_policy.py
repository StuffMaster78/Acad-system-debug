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
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        if attachment.visibility in {
            FileVisibility.PUBLIC,
            FileVisibility.CMS_PUBLIC,
        }:
            return True

        obj = attachment.content_object

        if obj is None:
            return False

        return self._is_enrolled_or_owner(user=user, obj=obj)

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
        """
        Return whether the user appears related to the class object.
        """

        user_id = getattr(user, "id", None)

        for attr_name in ("client_id", "owner_id", "user_id"):
            if getattr(obj, attr_name, None) == user_id:
                return True

        enrollments = getattr(obj, "enrollments", None)

        if enrollments is None:
            return False

        try:
            return enrollments.filter(user_id=user_id).exists()
        except AttributeError:
            return False