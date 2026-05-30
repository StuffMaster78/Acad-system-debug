from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class EditorFilePolicy(BaseFilePolicy):
    """
    Access policy for files attached to editor management objects.

    Editors are internal staff. They can view and download files they
    need for quality review (drafts, finals, revision files) but cannot
    delete or replace files — only full staff can do that.
    """

    domain_key = "editors"

    EDITOR_APP_LABELS = {
        "editor_management",
        "editors",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        return (
            attachment.content_type.app_label.lower() in self.EDITOR_APP_LABELS
        )

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        # Editors (is_editor attribute) can view non-private files.
        if getattr(user, "is_editor", False):
            return attachment.visibility not in {
                FileVisibility.PRIVATE,
                FileVisibility.INTERNAL_ONLY,
            }

        return False

    def can_replace(self, *, user, attachment: FileAttachment) -> bool:
        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    def can_request_deletion(
        self, *, user, attachment: FileAttachment
    ) -> bool:
        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )
