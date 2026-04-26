from __future__ import annotations

from files_management.enums import (
    ExternalFileReviewStatus,
    FileAccessAction,
    FileLifecycleStatus,
    FileScanStatus,
)
from files_management.exceptions import FileAccessDenied, FileNotAvailable
from files_management.models import FileAttachment, ManagedFile
from files_management.policies import FilePolicyRegistry
from files_management.selectors import FileAccessGrantSelector


class FileAccessService:
    """
    Central gatekeeper for file access decisions.

    Flow:
        1. Validate authentication and tenant scope
        2. Validate file lifecycle and scan status
        3. Validate external link review
        4. Check explicit access grants
        5. Delegate to domain policy
        6. Fallback to default policy

    This keeps the system safe while allowing domain apps to define
    real business rules.
    """

    BLOCKED_LIFECYCLE_STATUSES = {
        FileLifecycleStatus.QUARANTINED,
        FileLifecycleStatus.DELETED,
    }

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    @classmethod
    def ensure_can_access(
        cls,
        *,
        user,
        website,
        attachment: FileAttachment,
        action: str | FileAccessAction,
    ) -> None:
        """
        Raise when access is not allowed.
        """

        if not cls.can_access(
            user=user,
            website=website,
            attachment=attachment,
            action=action,
        ):
            raise FileAccessDenied(
                "You are not allowed to access this file."
            )

    @classmethod
    def can_access(
        cls,
        *,
        user,
        website,
        attachment: FileAttachment,
        action: str | FileAccessAction,
    ) -> bool:
        """
        Return whether the user can perform an action.
        """

        # Step 1: basic checks
        if not cls._is_authenticated(user=user):
            return False

        if attachment.website_id != website.id:
            return False

        if not attachment.is_active:
            return False

        # Step 2: file availability
        try:
            cls.ensure_source_available(attachment=attachment)
        except FileNotAvailable:
            return False

        # Step 3: superuser bypass
        if cls._is_superuser(user=user):
            return True

        # Step 4: explicit grants override
        if cls._has_explicit_grant(
            user=user,
            website=website,
            attachment=attachment,
            action=action,
        ):
            return True

        # Step 5: domain policy
        policy = FilePolicyRegistry.get_policy(
            attachment=attachment,
        )

        if policy:
            return cls._evaluate_policy(
                policy=policy,
                user=user,
                attachment=attachment,
                action=action,
            )

        return False

    # ---------------------------------------------------------
    # Source availability
    # ---------------------------------------------------------

    @classmethod
    def ensure_source_available(
        cls,
        *,
        attachment: FileAttachment,
    ) -> None:
        """
        Raise if file source is not usable.
        """

        if attachment.managed_file:
            cls._ensure_managed_file_available(
                managed_file=attachment.managed_file,
            )
            return

        if attachment.external_link:
            cls._ensure_external_link_available(
                attachment=attachment,
            )
            return

        raise FileNotAvailable("Attachment has no source.")

    @classmethod
    def _ensure_managed_file_available(
        cls,
        *,
        managed_file: ManagedFile,
    ) -> None:
        """
        Validate managed file lifecycle.
        """

        if managed_file.lifecycle_status in cls.BLOCKED_LIFECYCLE_STATUSES:
            raise FileNotAvailable("File is not available.")

        if managed_file.scan_status == FileScanStatus.FAILED:
            raise FileNotAvailable("File failed scanning.")

        if managed_file.scan_status == FileScanStatus.FLAGGED:
            raise FileNotAvailable("File flagged for review.")

    @staticmethod
    def _ensure_external_link_available(
        *,
        attachment: FileAttachment,
    ) -> None:
        """
        Validate external link review status.
        """

        link = attachment.external_link

        if not link or not link.is_active:
            raise FileNotAvailable("External link inactive.")

        if link.review_status != ExternalFileReviewStatus.APPROVED:
            raise FileNotAvailable("External link not approved.")

    # ---------------------------------------------------------
    # Policy evaluation
    # ---------------------------------------------------------

    @staticmethod
    def _evaluate_policy(
        *,
        policy,
        user,
        attachment: FileAttachment,
        action: str | FileAccessAction,
    ) -> bool:
        """
        Map action → policy method.
        """

        if action == FileAccessAction.VIEW:
            return policy.can_view(user=user, attachment=attachment)

        if action == FileAccessAction.PREVIEW:
            return policy.can_preview(user=user, attachment=attachment)

        if action == FileAccessAction.DOWNLOAD:
            return policy.can_download(user=user, attachment=attachment)

        if action == FileAccessAction.REPLACE:
            return policy.can_replace(user=user, attachment=attachment)

        if action == FileAccessAction.DELETE:
            return policy.can_delete(user=user, attachment=attachment)

        return False

    # ---------------------------------------------------------
    # Grants
    # ---------------------------------------------------------

    @classmethod
    def _has_explicit_grant(
        cls,
        *,
        user,
        website,
        attachment: FileAttachment,
        action: str | FileAccessAction,
    ) -> bool:
        """
        Check explicit access grants.
        """

        if not attachment.managed_file:
            return False

        return FileAccessGrantSelector.has_active_grant(
            user=user,
            website=website,
            managed_file=attachment.managed_file,
            attachment=attachment,
            action=str(action),
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _is_authenticated(*, user) -> bool:
        return bool(
            user and getattr(user, "is_authenticated", False)
        )

    @staticmethod
    def _is_superuser(*, user) -> bool:
        return bool(getattr(user, "is_superuser", False))