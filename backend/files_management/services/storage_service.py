"""
StorageService — unified interface to DigitalOcean Spaces.

Every file upload, download, deletion, and signed-URL generation in the
entire system goes through this class.  Other apps NEVER touch boto3
directly.

Usage:
    from files_management.services.storage_service import StorageService

    managed_file = StorageService.upload(
        file_obj=request.FILES["document"],
        bucket=bucket,
        website=website,
        uploaded_by=request.user,
        file_kind=FileKind.CMS_ATTACHMENT,
    )

    url = StorageService.generate_signed_url(managed_file, expires_in=600)
    StorageService.delete(managed_file, hard=True)
"""

from __future__ import annotations

import hashlib
import logging
import mimetypes
import os
import uuid as uuid_lib
from io import BytesIO
from typing import TYPE_CHECKING, BinaryIO
from typing import Any, cast

from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

from files_management.models.file_quota import FileQuota
from files_management.models.managed_file import ManagedFile

if TYPE_CHECKING:
    from files_management.models.file_bucket import FileBucket
    from files_management.models.managed_file import ManagedFile

logger = logging.getLogger(__name__)


class StorageService:
    """Unified interface to DigitalOcean Spaces (S3-compatible)."""

    # ----------------------------------------------------------------
    # Client
    # ----------------------------------------------------------------

    @staticmethod
    def _get_client(bucket: FileBucket):
        """Return a boto3 S3 client configured for the bucket's region."""
        import boto3

        return boto3.client(
            "s3",
            region_name=bucket.spaces_region,
            endpoint_url=f"https://{bucket.spaces_region}.digitaloceanspaces.com",
            aws_access_key_id=getattr(settings, "DO_SPACES_KEY", ""),
            aws_secret_access_key=getattr(settings, "DO_SPACES_SECRET", ""),
            config=Config(signature_version="s3v4"),
        )

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    @classmethod
    def upload(
        cls,
        file_obj: UploadedFile | BinaryIO,
        bucket: FileBucket,
        website,
        uploaded_by=None,
        file_kind: str = "other",
        content_object=None,
        retention_policy: str = "forever",
        is_public: bool | None = None,
        skip_scan: bool = False,
        skip_derivatives: bool = False,
    ) -> ManagedFile:
        """
        Full upload pipeline:
        1. Compute SHA-256 for dedup
        2. Check for existing identical file (same hash + tenant + bucket)
        3. Validate size against bucket limits and tenant quota
        4. Upload bytes to Spaces
        5. Create ManagedFile record
        6. Queue virus scan
        7. Queue derivative generation
        """
        from django.contrib.contenttypes.models import ContentType

        from files_management.enums import (
            FileKind,
            FileLifecycleStatus,
            FileScanStatus,
        )
        from files_management.models.file_access_log import FileAccessLog
        from files_management.models.file_quota import FileQuota
        from files_management.models.managed_file import ManagedFile

        # ---- Metadata ----
        filename = getattr(file_obj, "name", "unknown")
        file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        raw_size = getattr(file_obj, "size", 0)
        size = int(raw_size or 0)
        mime = (
            getattr(file_obj, "content_type", None)
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )

        # ---- 1. SHA-256 ----
        sha256 = cls._sha256(file_obj)
        file_obj.seek(0)

        # ---- 2. Dedup check ----
        existing = ManagedFile.objects.filter(
            website=website,
            bucket=bucket,
            sha256_hash=sha256,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
        ).first()

        if existing:
            logger.info(
                "Dedup hit: reusing ManagedFile %s for %s",
                existing.uuid,
                filename,
            )
            return existing

        # ---- 3. Validate sizes ----
        if size and bucket.max_file_size_bytes and size > bucket.max_file_size_bytes:
            raise ValueError(
                f"File too large: {size:,} bytes "
                f"(bucket max: {bucket.max_file_size_bytes:,})"
            )

        quota, _ = FileQuota.objects.get_or_create(website=website)
        if size and quota.is_over_quota:
            raise ValueError(
                f"Tenant '{website}' has exceeded its storage quota "
                f"({quota.usage_percent:.0f}% used)"
            )

        # ---- 4. Build storage key and upload ----
        file_uuid = uuid_lib.uuid4()
        prefix = bucket.spaces_path_prefix.strip("/")
        tenant_slug = getattr(website, "slug", str(website.pk))
        storage_key = f"{prefix}/{tenant_slug}/{file_uuid}.{file_ext}".lstrip("/")

        client = cls._get_client(bucket)
        extra_args: dict = {"ContentType": mime}

        file_is_public = is_public if is_public is not None else bucket.is_public
        if file_is_public:
            extra_args["ACL"] = "public-read"

        try:
            file_obj.seek(0)
            client.upload_fileobj(
                file_obj,
                bucket.spaces_bucket_name,
                storage_key,
                ExtraArgs=extra_args,
            )
        except ClientError as exc:
            logger.error("Spaces upload failed for %s: %s", filename, exc)
            raise RuntimeError(f"Storage upload failed: {exc}") from exc

        # ---- 5. Create record ----
        ct = None
        obj_id = None
        if content_object is not None:
            ct = ContentType.objects.get_for_model(content_object)
            obj_id = content_object.pk

        managed_file = ManagedFile.objects.create(
            uuid=file_uuid,
            website=website,
            uploaded_by=uploaded_by,
            bucket=bucket,
            file=file_obj if isinstance(file_obj, UploadedFile) else None,
            storage_key=storage_key,
            original_filename=filename,
            file_size_bytes=size,
            mime_type=mime,
            file_extension=file_ext,
            file_kind=file_kind,
            sha256_hash=sha256,
            is_public=file_is_public,
            lifecycle_status=FileLifecycleStatus.PROCESSING,
            scan_status=FileScanStatus.NOT_SCANNED,
            retention_policy=retention_policy,
            content_type=ct,
            object_id=obj_id,
        )

        # ---- Update quota ----
        if size:
            FileQuota.objects.filter(pk=quota.pk).update(
                current_size_bytes=quota.current_size_bytes + size,
                current_files_count=quota.current_files_count + 1,
            )

        # ---- Audit log ----
        FileAccessLog.objects.create(
            file=managed_file,
            access_type="upload",
            user=uploaded_by,
            bytes_transferred=size,
        )

        # ---- 6 & 7. Async tasks ----
        from files_management.tasks import (
            generate_derivatives,
            scan_file_for_viruses,
        )
        scan_task = cast(Any, scan_file_for_viruses)
        derivative_task = cast(Any, generate_derivatives)

        if not skip_scan:
            scan_task.delay(managed_file.pk)
        else:
            managed_file.scan_status = FileScanStatus.SKIPPED
            managed_file.lifecycle_status = FileLifecycleStatus.ACTIVE
            managed_file.save(
                update_fields=[
                    "scan_status",
                    "lifecycle_status",
                ]
            )

        if not skip_derivatives:
            derivative_task.delay(managed_file.pk)

        # if not skip_scan:
        #     scan_file_for_viruses.delay(managed_file.pk)
        # else:
        #     managed_file.scan_status = FileScanStatus.SKIPPED
        #     managed_file.lifecycle_status = FileLifecycleStatus.ACTIVE
        #     managed_file.save(update_fields=["scan_status", "lifecycle_status"])

        # if not skip_derivatives:
        #     generate_derivatives.delay(managed_file.pk)

        logger.info(
            "Uploaded %s → %s (%s, %s bytes)",
            filename,
            storage_key,
            managed_file.uuid,
            size,
        )
        return managed_file

    # ------------------------------------------------------------------
    # Signed URLs
    # ------------------------------------------------------------------

    @classmethod
    def generate_signed_url(
        cls,
        managed_file: ManagedFile,
        expires_in: int | None = None,
        force_download: bool = False,
    ) -> str:
        """Generate a time-limited pre-signed URL for private files."""
        bucket = managed_file.bucket
        client = cls._get_client(bucket)
        expiry = expires_in or bucket.signed_url_expiry_seconds or 3600

        params: dict = {
            "Bucket": bucket.spaces_bucket_name,
            "Key": managed_file.storage_key,
        }
        if force_download:
            params["ResponseContentDisposition"] = (
                f'attachment; filename="{managed_file.original_filename}"'
            )

        try:
            url = client.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expiry,
            )
            return url
        except ClientError as exc:
            logger.error(
                "Signed URL generation failed for %s: %s",
                managed_file.uuid,
                exc,
            )
            raise RuntimeError(f"Signed URL generation failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Download URL (public or signed)
    # ------------------------------------------------------------------

    @classmethod
    def get_download_url(
        cls,
        managed_file: ManagedFile,
        force_download: bool = False,
    ) -> str:
        """Return the best URL for a file — CDN if public, signed if private."""
        if managed_file.is_public and managed_file.public_url:
            return managed_file.public_url
        return cls.generate_signed_url(
            managed_file,
            force_download=force_download,
        )

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    @classmethod
    def delete(cls, managed_file: ManagedFile, hard: bool = False) -> None:
        """
        Soft-delete by default (set lifecycle_status=DELETED, record deleted_at).
        Hard-delete removes from Spaces and the database.
        """
        from files_management.enums import FileLifecycleStatus
        from files_management.models.file_access_log import FileAccessLog
        from files_management.models.file_quota import FileQuota

        if hard:
            # Remove from storage
            try:
                client = cls._get_client(managed_file.bucket)
                client.delete_object(
                    Bucket=managed_file.bucket.spaces_bucket_name,
                    Key=managed_file.storage_key,
                )
            except ClientError as exc:
                logger.warning(
                    "Spaces delete failed for %s (may already be gone): %s",
                    managed_file.uuid,
                    exc,
                )

            # Delete derivatives first
            derivatives = cast(Any, managed_file).derivatives.all()

            for derivative in derivatives:
                cls.delete(derivative, hard=True)

            # Update quota
            try:
                quota = FileQuota.objects.get(website=managed_file.website)
                FileQuota.objects.filter(pk=quota.pk).update(
                    current_size_bytes=max(
                        0, quota.current_size_bytes - managed_file.file_size_bytes
                    ),
                    current_files_count=max(0, quota.current_files_count - 1),
                )
            except FileQuota.DoesNotExist:
                pass

            # Audit
            FileAccessLog.objects.create(
                file=managed_file,
                access_type="delete",
                user=None,
            )

            logger.info("Hard-deleted %s", managed_file.uuid)
            managed_file.delete()

        else:
            managed_file.lifecycle_status = FileLifecycleStatus.DELETED
            managed_file.deleted_at = timezone.now()
            managed_file.save(update_fields=["lifecycle_status", "deleted_at"])
            logger.info("Soft-deleted %s", managed_file.uuid)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sha256(file_obj) -> str:
        """Stream-compute SHA-256."""
        h = hashlib.sha256()
        for chunk in iter(lambda: file_obj.read(8192), b""):
            h.update(chunk)
        file_obj.seek(0)
        return h.hexdigest()
