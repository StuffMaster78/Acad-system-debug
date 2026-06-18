from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from files_management.enums import FileAccessAction, FilePurpose
from files_management.exceptions import FileNotAvailable
from files_management.models.file_attachment import FileAttachment
from files_management.models.file_download_log import FileDownloadLog
from files_management.services.file_access_service import FileAccessService
from files_management.services.file_delivery_guard_service import (
    FileDeliveryGuardService,
    GUARDED_PURPOSES,
)
from files_management.models.file_download_receipt import FileDownloadReceipt
from files_management.signals import file_first_downloaded
from files_management.storage import SignedUrlBuilder


class FileDownloadService:
    """
    Handles safe file download URL generation.

    Downloads must always pass through access checks. For uploaded files,
    this service returns a storage URL and records a download log. For
    external links, it returns the approved external URL.

    For ORDER_FINAL and milestone files, a delivery guard check runs after
    the access check. A blocked guard raises FileDeliveryBlocked with a
    structured reason the API layer can return to the client.
    """

    @classmethod
    @transaction.atomic
    def get_download_url(
        cls,
        *,
        user,
        website,
        attachment: FileAttachment,
        ip_address: str = "",
        user_agent: str = "",
        order=None,
    ) -> str:
        """
        Return a download URL after access and delivery guard checks.

        Args:
            user: Requesting user.
            website: Tenant website.
            attachment: File attachment to download.
            ip_address: Client IP for audit log.
            user_agent: Client agent for audit log.
            order: Domain order object, passed to the delivery guard
                        for balance checking. Required for guarded files.

        Raises:
            FileAccessDenied: User lacks role/visibility access.
            FileDeliveryBlocked: Guard check failed (balance, scan, etc.).
            FileNotAvailable: File is quarantined or has no source.
        """
        FileAccessService.ensure_can_access(
            user=user,
            website=website,
            attachment=attachment,
            action=FileAccessAction.DOWNLOAD,
        )

        if attachment.purpose in GUARDED_PURPOSES:
            FileDeliveryGuardService.check_and_raise(
                attachment=attachment,
                user=user,
                order=order,
            )

        if attachment.managed_file:
            download_url = cls._get_managed_file_download_url(
                user=user,
                attachment=attachment,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        elif attachment.external_link:
            download_url = attachment.external_link.url
        else:
            raise FileNotAvailable(
                "Attachment has no downloadable source."
            )

        # Clear this attachment's "new" state only for the requesting user.
        # This applies to both uploaded files and approved external links.
        FileDownloadReceipt.objects.get_or_create(
            attachment=attachment,
            user=user,
        )

        return download_url

    @classmethod
    def _get_managed_file_download_url(
        cls,
        *,
        user,
        attachment: FileAttachment,
        ip_address: str = "",
        user_agent: str = "",
    ) -> str:
        """
        Generate a signed URL for an uploaded file and record download logs.

        Also stamps first_downloaded_at on the attachment the first time a
        client downloads successfully.
        """
        managed_file = attachment.managed_file

        if managed_file is None:
            raise FileNotAvailable("Managed file is not available.")

        download_url = SignedUrlBuilder.build_url(
            storage_name=managed_file.storage_key,
        )

        FileDownloadLog.objects.create(
            file=managed_file,
            downloaded_by=user,
            ip_address=ip_address or None,
            user_agent=user_agent,
        )

        # Stamp global first-download timestamp once.
        if attachment.first_downloaded_at is None:
            attachment.first_downloaded_at = timezone.now()
            attachment.save(update_fields=["first_downloaded_at", "updated_at"])
            file_first_downloaded.send(
                sender=attachment.__class__,
                attachment=attachment,
                user=user,
            )

        return download_url
