from __future__ import annotations

from abc import ABC, abstractmethod

from files_management.models import FileAttachment


class BaseFilePolicy(ABC):
    """
    Base contract for domain specific file access policies.

    Domain policies answer business access questions for attachments.
    They should not generate URLs, mutate files, or write audit logs.

    Examples:
        Order policy decides if assigned writer can download files.
        Message policy decides if conversation participant can view them.
        CMS policy decides if public content files are visible.
    """

    domain_key: str = "default"

    @abstractmethod
    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether this policy can evaluate the attachment.
        """

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can view attachment metadata.
        """

        return False

    def can_preview(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can preview the attachment.
        """

        return self.can_view(user=user, attachment=attachment)

    def can_download(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can download the attachment source.
        """

        return self.can_view(user=user, attachment=attachment)

    def can_replace(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can replace the attachment source.
        """

        return False

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Return whether the user can request deletion.

        Clients and writers should usually request deletion instead of
        deleting files directly.
        """

        return False

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can directly delete the attachment.
        """

        return False

    @staticmethod
    def is_staff_like(*, user) -> bool:
        """
        Return whether the user appears to be staff/admin.

        This helper is intentionally defensive because role naming may
        differ across apps during refactors.
        """

        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_super_admin", False)
        )

    @staticmethod
    def is_same_website(*, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user belongs to the attachment website.
        """

        return getattr(user, "website_id", None) == attachment.website.id

    @staticmethod
    def is_uploader(*, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user uploaded or attached the file.
        """

        user_id = getattr(user, "id", None)

        if attachment.attached_by_id == user_id:
            return True

        if attachment.managed_file_id:
            return attachment.managed_file.uploaded_by_id == user_id

        if attachment.external_link_id:
            return attachment.external_link.submitted_by_id == user_id

        return False