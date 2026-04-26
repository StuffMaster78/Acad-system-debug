from __future__ import annotations

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FileLifecycleStatus, FileScanStatus
from files_management.models import ManagedFile
from files_management.services.file_policy_service import FilePolicyService
from files_management.storage import (
    FileStorageBackend,
    FileStoragePathBuilder,
    MimeTypeDetector,
)
from files_management.validators import normalize_filename


class FileUploadService:
    """
    Handles validated file upload creation.

    This service creates ManagedFile records and stores uploaded content
    through the configured Django storage backend. It does not attach the
    file to business objects. Attachment is handled separately by
    FileAttachmentService.
    """

    @classmethod
    @transaction.atomic
    def upload_file(
        cls,
        *,
        website,
        uploaded_by,
        uploaded_file: UploadedFile,
        purpose: str,
        is_public: bool = False,
        metadata: dict | None = None,
    ) -> ManagedFile:
        """
        Validate, store, and register an uploaded file.

        Args:
            website:
                Tenant that owns the file.
            uploaded_by:
                User who uploaded the file.
            uploaded_file:
                Django uploaded file object.
            purpose:
                Intended attachment purpose.
            is_public:
                Whether the file may be public.
            metadata:
                Optional metadata to store on the file.

        Returns:
            The created ManagedFile record.
        """

        original_name = normalize_filename(uploaded_file.name)

        mime_type = FilePolicyService.validate_uploaded_file(
            website=website,
            purpose=purpose,
            uploaded_file=uploaded_file,
        )

        storage_key = FileStoragePathBuilder.build_key(
            website_id=website.id,
            original_name=original_name,
            purpose=purpose,
        )

        saved_name = FileStorageBackend.save(
            storage_key=storage_key,
            content=uploaded_file,
        )

        file_kind = MimeTypeDetector.detect_kind(
            mime_type=mime_type,
            filename=original_name,
        )

        return ManagedFile.objects.create(
            website=website,
            uploaded_by=uploaded_by,
            file=saved_name,
            original_name=original_name,
            file_size=uploaded_file.size,
            mime_type=mime_type,
            file_kind=file_kind,
            storage_key=saved_name,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
            scan_status=FileScanStatus.NOT_SCANNED,
            is_public=is_public,
            metadata=metadata or {},
        )