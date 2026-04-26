from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import Max

from files_management.enums import FileAccessAction
from files_management.exceptions import FileVersionError
from files_management.models import FileAttachment, FileVersion, ManagedFile
from files_management.services.file_access_service import FileAccessService
from files_management.services.file_upload_service import FileUploadService


class FileVersionService:
    """
    Handles safe replacement and version tracking for files.

    Versioning is important for drafts, final deliverables, CMS assets,
    profile images, writer samples, and any file that may be replaced
    while preserving history.
    """

    @classmethod
    @transaction.atomic
    def replace_attachment_file(
        cls,
        *,
        website,
        replaced_by,
        attachment: FileAttachment,
        uploaded_file: UploadedFile,
        notes: str = "",
        metadata: dict | None = None,
    ) -> FileAttachment:
        """
        Replace the uploaded file behind an existing attachment.

        The old file remains in storage and is referenced by FileVersion.
        The attachment now points to the new ManagedFile.
        """

        if attachment.website.id != website.id:
            raise FileVersionError(
                "Attachment does not belong to this website."
            )

        if attachment.managed_file is None:
            raise FileVersionError(
                "Only uploaded file attachments can be replaced."
            )

        FileAccessService.ensure_can_access(
            user=replaced_by,
            website=website,
            attachment=attachment,
            action=FileAccessAction.REPLACE,
        )

        old_file = attachment.managed_file

        new_file = FileUploadService.upload_file(
            website=website,
            uploaded_by=replaced_by,
            uploaded_file=uploaded_file,
            purpose=attachment.purpose,
            is_public=old_file.is_public,
            metadata=metadata or old_file.metadata,
        )

        version_number = cls.get_next_version_number(
            managed_file=new_file,
        )

        FileVersion.objects.create(
            file=new_file,
            version_number=version_number,
            replaced_file=old_file,
            created_by=replaced_by,
            notes=notes,
        )

        attachment.managed_file = new_file
        
        attachment.full_clean()
        attachment.save(
            update_fields=[
                "managed_file",
                "updated_at",
            ]
        )

        return attachment

    @classmethod
    def create_initial_version(
        cls,
        *,
        managed_file: ManagedFile,
        created_by=None,
        notes: str = "",
    ) -> FileVersion:
        """
        Create the first version record for a managed file.
        """

        existing = FileVersion.objects.filter(
            file=managed_file,
            version_number=1,
        ).first()

        if existing:
            return existing

        return FileVersion.objects.create(
            file=managed_file,
            version_number=1,
            replaced_file=None,
            created_by=created_by,
            notes=notes,
        )

    @staticmethod
    def get_next_version_number(
        *,
        managed_file: ManagedFile,
    ) -> int:
        """
        Return the next version number for a managed file.
        """

        result = FileVersion.objects.filter(
            file=managed_file,
        ).aggregate(
            max_version=Max("version_number"),
        )

        max_version = result.get("max_version") or 0
        return int(max_version) + 1