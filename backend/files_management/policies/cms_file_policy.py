from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class CmsFilePolicy(BaseFilePolicy):
    """
    Access policy for CMS, SEO, blog, and marketing files.

    Public content assets may be visible publicly. Draft, unpublished,
    internal, and reusable content assets should stay staff controlled.
    """

    domain_key = "cms"

    CMS_APP_LABELS = {
        "cms",
        "cms_content",
        "seo_pages",
        "blog_pages_management",
        "service_pages_management",
        "media_management",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether this attachment belongs to a content app.
        """

        return attachment.content_type.app_label.lower() in self.CMS_APP_LABELS

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can view a CMS file.
        """

        if attachment.visibility in {
            FileVisibility.PUBLIC,
            FileVisibility.CMS_PUBLIC,
        }:
            return True

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        return self.is_staff_like(user=user)

    def can_replace(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow tenant staff to replace CMS files.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow tenant staff to request deletion.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow staff deletion through controlled workflows.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )