from __future__ import annotations

import hashlib

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.enums import FileLifecycleStatus, FileScanStatus
from files_management.models.file_bucket import FileBucket
from files_management.models.managed_file import ManagedFile
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

        original_filename = normalize_filename(uploaded_file.name)
        file_extension = (
            original_filename.rsplit(".", 1)[-1].lower()
            if "." in original_filename
            else ""
        )

        mime_type = FilePolicyService.validate_uploaded_file(
            website=website,
            purpose=purpose,
            uploaded_file=uploaded_file,
        )

        bucket = cls._get_default_bucket(is_public=is_public)

        storage_key = FileStoragePathBuilder.build_key(
            website_id=website.id,
            original_name=original_filename,
            purpose=purpose,
        )

        sha256_hash = cls._sha256(uploaded_file)
        uploaded_file.seek(0)

        saved_name = FileStorageBackend.save(
            storage_key=storage_key,
            content=uploaded_file,
        )

        file_kind = MimeTypeDetector.detect_kind(
            mime_type=mime_type,
            filename=original_filename,
        )

        return ManagedFile.objects.create(
            website=website,
            uploaded_by=uploaded_by,
            bucket=bucket,
            file=saved_name,
            original_filename=original_filename,
            file_size_bytes=uploaded_file.size,
            mime_type=mime_type,
            file_extension=file_extension,
            file_kind=file_kind,
            sha256_hash=sha256_hash,
            storage_key=saved_name,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
            scan_status=FileScanStatus.NOT_SCANNED,
            is_public=is_public,
            metadata=metadata or {},
        )

    @staticmethod
    def _get_default_bucket(*, is_public: bool) -> FileBucket:
        bucket_type = "tenant_public" if is_public else "tenant_private"
        bucket = FileBucket.objects.filter(bucket_type=bucket_type).first()
        if bucket:
            return bucket
        fallback = FileBucket.objects.first()
        if fallback:
            return fallback
        raise ValueError("No file bucket configured.")

    @staticmethod
    def _sha256(uploaded_file: UploadedFile) -> str:
        hasher = hashlib.sha256()
        uploaded_file.seek(0)
        for chunk in uploaded_file.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()
