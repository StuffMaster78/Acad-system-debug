from __future__ import annotations

from files_management.enums import FilePurpose, FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class ProfileFilePolicy(BaseFilePolicy):
    """
    Access policy for profile and identity related files.

    Public profile images can be visible broadly. Verification documents,
    contracts, certificates, and internal profile files should remain
    restricted to owners and staff.
    """

    domain_key = "profiles"

    PROFILE_MODEL_NAMES = {
        "userprofile",
        "writerprofile",
        "clientprofile",
        "profile",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether the attachment belongs to a profile object.
        """

        model_name = attachment.content_type.model.lower()
        app_label = attachment.content_type.app_label.lower()

        return (
            app_label in {"users", "accounts", "profiles"}
            or model_name in self.PROFILE_MODEL_NAMES
        )

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user can view a profile file.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if attachment.purpose in {
            FilePurpose.PROFILE_AVATAR,
            FilePurpose.PROFILE_PHOTO,
        }:
            if attachment.visibility in {
                FileVisibility.PUBLIC,
                FileVisibility.CMS_PUBLIC,
            }:
                return True

        if self.is_staff_like(user=user):
            return True

        return self._is_profile_owner(user=user, attachment=attachment)

    def can_replace(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow owner or staff to replace profile files.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        return (
            self.is_staff_like(user=user)
            or self._is_profile_owner(user=user, attachment=attachment)
        )

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow owners to request deletion.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        return (
            self.is_staff_like(user=user)
            or self._is_profile_owner(user=user, attachment=attachment)
        )

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Only staff may directly delete profile files.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    @staticmethod
    def _is_profile_owner(*, user, attachment: FileAttachment) -> bool:
        """
        Return whether the user owns the profile object.
        """

        obj = attachment.content_object

        if obj is None:
            return False

        user_id = getattr(user, "id", None)

        if getattr(obj, "user_id", None) == user_id:
            return True

        return getattr(obj, "id", None) == user_id