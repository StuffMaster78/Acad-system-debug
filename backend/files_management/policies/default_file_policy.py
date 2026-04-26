from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class DefaultFilePolicy(BaseFilePolicy):
    """
    Fallback policy for attachments without a domain specific policy.

    This policy is intentionally conservative. It allows public files,
    uploader-owned private files, and staff access within tenant bounds.
    """

    domain_key = "default"

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return True for all attachments as a fallback policy.
        """

        return True

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Evaluate basic generic visibility rules.
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

        if attachment.visibility in {
            FileVisibility.PRIVATE,
            FileVisibility.OWNER_ONLY,
        }:
            return self.is_uploader(user=user, attachment=attachment)

        return False

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow uploaders to request deletion.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        return self.is_uploader(user=user, attachment=attachment)

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Only staff-like users may directly delete through controlled flows.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )