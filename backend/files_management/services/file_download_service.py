from __future__ import annotations

from django.db import transaction

from files_management.enums import FileAccessAction
from files_management.exceptions import FileNotAvailable
from files_management.models import FileAttachment, FileDownloadLog
from files_management.services.file_access_service import FileAccessService
from files_management.storage import SignedUrlBuilder


class FileDownloadService:
    """
    Handles safe file download URL generation.

    Downloads must always pass through access checks. For uploaded files,
    this service returns a storage URL and records a download log. For
    external links, it returns the approved external URL.
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
    ) -> str:
        """
        Return a download URL after access checks and audit logging.
        """

        FileAccessService.ensure_can_access(
            user=user,
            website=website,
            attachment=attachment,
            action=FileAccessAction.DOWNLOAD,
        )

        if attachment.managed_file:
            return cls._get_managed_file_download_url(
                user=user,
                attachment=attachment,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        if attachment.external_link:
            return attachment.external_link.url

        raise FileNotAvailable("Attachment has no downloadable source.")

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
        Generate a URL for an uploaded file and record a download log.
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

        return download_url