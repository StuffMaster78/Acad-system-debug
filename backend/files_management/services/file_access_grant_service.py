from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from files_management.exceptions import FileAccessDenied
from files_management.models import FileAccessGrant, FileAttachment


class FileAccessGrantService:
    """
    Handles explicit file access grants.

    Grants are controlled exceptions to normal domain policy. They are
    useful for support, dispute review, writer replacement, temporary
    client access, and admin guided workflows.

    Grants should not replace normal order, message, CMS, profile, or
    support policies.
    """

    @classmethod
    @transaction.atomic
    def grant_access(
        cls,
        *,
        website,
        managed_file,
        grantee,
        granted_by,
        action: str,
        attachment: FileAttachment | None = None,
        reason: str = "",
        expires_at=None,
    ) -> FileAccessGrant:
        """
        Grant a user explicit access to a managed file.
        """

        cls._ensure_staff_actor(
            actor=granted_by,
            website=website,
        )

        if managed_file.website_id != website.id:
            raise FileAccessDenied(
                "Managed file does not belong to this website."
            )

        if attachment and attachment.website_id != website.id:
            raise FileAccessDenied(
                "Attachment does not belong to this website."
            )

        return FileAccessGrant.objects.create(
            website=website,
            managed_file=managed_file,
            attachment=attachment,
            grantee=grantee,
            granted_by=granted_by,
            action=action,
            reason=reason,
            expires_at=expires_at,
        )

    @classmethod
    @transaction.atomic
    def revoke_access(
        cls,
        *,
        access_grant: FileAccessGrant,
        revoked_by,
    ) -> FileAccessGrant:
        """
        Revoke an active access grant.
        """

        cls._ensure_staff_actor(
            actor=revoked_by,
            website=access_grant.website,
        )

        if access_grant.revoked_at:
            return access_grant

        access_grant.revoked_at = timezone.now()
        access_grant.revoked_by = revoked_by
        access_grant.full_clean()
        access_grant.save(
            update_fields=[
                "revoked_at",
                "revoked_by",
            ]
        )

        return access_grant

    @staticmethod
    def _ensure_staff_actor(*, actor, website) -> None:
        """
        Ensure the actor can manage access grants.
        """

        is_staff = bool(
            getattr(actor, "is_staff", False)
            or getattr(actor, "is_superuser", False)
            or getattr(actor, "is_admin", False)
            or getattr(actor, "is_super_admin", False)
        )

        same_website = getattr(actor, "website_id", None) == website.id

        if not is_staff or not same_website:
            raise FileAccessDenied(
                "Only tenant staff can manage file access grants."
            )