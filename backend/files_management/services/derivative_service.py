"""
Derivative Service
====================

Generates derived versions of uploaded files:
    • thumbnail_sm  — 150×150 px
    • thumbnail_md  — 400×400 px
    • thumbnail_lg  — 800×800 px
    • webp           — WebP version of images (smaller, faster)
    • preview_pdf    — first-page render of PDFs as PNG

Dependencies:
    pip install Pillow

For PDF previews (optional, install if needed):
    apt-get install poppler-utils   # for pdf2image
    pip install pdf2image

Each derivative is stored as its own ManagedFile with
``parent_file`` pointing to the original and ``derivative_type``
set appropriately.
"""

from __future__ import annotations

import logging
import uuid as uuid_lib
from io import BytesIO
from typing import TYPE_CHECKING

from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from files_management.models import ManagedFile

logger = logging.getLogger(__name__)

# Thumbnail dimensions
THUMBNAIL_SIZES = {
    "thumbnail_sm": (150, 150),
    "thumbnail_md": (400, 400),
    "thumbnail_lg": (800, 800),
}


class DerivativeService:
    """Generate derived file versions (thumbnails, WebP, PDF previews)."""

    @classmethod
    def generate_all(cls, managed_file: ManagedFile) -> list:
        """
        Generate all applicable derivatives for a file.
        Returns list of created ManagedFile derivative records.
        """
        derivatives = []

        mime = managed_file.mime_type or ""

        if mime.startswith("image/"):
            # Generate thumbnails
            for deriv_type, size in THUMBNAIL_SIZES.items():
                try:
                    deriv = cls._generate_image_thumbnail(
                        managed_file, deriv_type, size
                    )
                    if deriv:
                        derivatives.append(deriv)
                except Exception as exc:
                    logger.error(
                        "Thumbnail %s generation failed for %s: %s",
                        deriv_type,
                        managed_file.uuid,
                        exc,
                    )

            # Generate WebP version (if source isn't already WebP)
            if mime != "image/webp":
                try:
                    deriv = cls._generate_webp(managed_file)
                    if deriv:
                        derivatives.append(deriv)
                except Exception as exc:
                    logger.error(
                        "WebP generation failed for %s: %s",
                        managed_file.uuid,
                        exc,
                    )

        elif mime == "application/pdf":
            # Generate PDF preview (first page as PNG)
            try:
                deriv = cls._generate_pdf_preview(managed_file)
                if deriv:
                    derivatives.append(deriv)
            except Exception as exc:
                logger.error(
                    "PDF preview generation failed for %s: %s",
                    managed_file.uuid,
                    exc,
                )

        if derivatives:
            logger.info(
                "Generated %d derivatives for %s",
                len(derivatives),
                managed_file.uuid,
            )

        return derivatives

    @classmethod
    def _generate_image_thumbnail(
        cls,
        managed_file: ManagedFile,
        deriv_type: str,
        size: tuple[int, int],
    ) -> ManagedFile | None:
        """Create a thumbnail of the given size."""
        from PIL import Image

        # Skip if derivative already exists
        from files_management.models import ManagedFile as MF

        if MF.objects.filter(parent_file=managed_file, derivative_type=deriv_type).exists():
            return None

        image_bytes = cls._read_file_bytes(managed_file)
        if image_bytes is None:
            return None

        try:
            img = Image.open(BytesIO(image_bytes))

            # Convert to RGB if necessary (handles RGBA, P mode, etc.)
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

            # Use thumbnail (preserves aspect ratio, fits within size)
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save to buffer
            buffer = BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)

            return cls._save_derivative(
                parent=managed_file,
                file_bytes=buffer.getvalue(),
                derivative_type=deriv_type,
                mime_type="image/jpeg",
                extension="jpg",
                width=img.width,
                height=img.height,
            )
        except Exception as exc:
            logger.error("Image thumbnail error: %s", exc)
            return None

    @classmethod
    def _generate_webp(cls, managed_file: ManagedFile) -> ManagedFile | None:
        """Create a WebP version of an image."""
        from PIL import Image
        from files_management.models import ManagedFile as MF

        if MF.objects.filter(parent_file=managed_file, derivative_type="webp").exists():
            return None

        image_bytes = cls._read_file_bytes(managed_file)
        if image_bytes is None:
            return None

        try:
            img = Image.open(BytesIO(image_bytes))

            if img.mode not in ("RGB", "RGBA", "L"):
                img = img.convert("RGB")

            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=80, method=4)
            buffer.seek(0)

            return cls._save_derivative(
                parent=managed_file,
                file_bytes=buffer.getvalue(),
                derivative_type="webp",
                mime_type="image/webp",
                extension="webp",
                width=img.width,
                height=img.height,
            )
        except Exception as exc:
            logger.error("WebP conversion error: %s", exc)
            return None

    @classmethod
    def _generate_pdf_preview(
        cls, managed_file: ManagedFile
    ) -> ManagedFile | None:
        """Render the first page of a PDF as a PNG image."""
        from files_management.models import ManagedFile as MF

        if MF.objects.filter(parent_file=managed_file, derivative_type="preview_pdf").exists():
            return None

        pdf_bytes = cls._read_file_bytes(managed_file)
        if pdf_bytes is None:
            return None

        try:
            from pdf2image import convert_from_bytes  # type: ignore[import-untyped]

            images = convert_from_bytes(
                pdf_bytes,
                first_page=1,
                last_page=1,
                dpi=150,
                fmt="png",
            )

            if not images:
                return None

            img = images[0]
            buffer = BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)

            return cls._save_derivative(
                parent=managed_file,
                file_bytes=buffer.getvalue(),
                derivative_type="preview_pdf",
                mime_type="image/png",
                extension="png",
                width=img.width,
                height=img.height,
            )

        except ImportError:
            logger.warning(
                "pdf2image not installed — skipping PDF preview for %s. "
                "Install with: pip install pdf2image (requires poppler-utils)",
                managed_file.uuid,
            )
            return None
        except Exception as exc:
            logger.error("PDF preview error: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def _read_file_bytes(cls, managed_file: ManagedFile) -> bytes | None:
        """Read file content from storage."""
        try:
            if managed_file.file:
                managed_file.file.open("rb")
                data = managed_file.file.read()
                managed_file.file.close()
                return data
        except Exception:
            pass

        # Fallback: download from Spaces
        try:
            from files_management.services.storage_service import StorageService

            client = StorageService._get_client(managed_file.bucket)
            response = client.get_object(
                Bucket=managed_file.bucket.spaces_bucket_name,
                Key=managed_file.storage_key,
            )
            return response["Body"].read()
        except Exception as exc:
            logger.error("Could not read file %s: %s", managed_file.uuid, exc)
            return None

    @classmethod
    def _save_derivative(
        cls,
        parent: ManagedFile,
        file_bytes: bytes,
        derivative_type: str,
        mime_type: str,
        extension: str,
        width: int | None = None,
        height: int | None = None,
    ) -> ManagedFile:
        """Create a ManagedFile record for a derivative and upload to storage."""
        import hashlib

        from files_management.enums import (
            FileKind,
            FileLifecycleStatus,
            FileScanStatus,
        )
        from files_management.models import ManagedFile

        file_uuid = uuid_lib.uuid4()
        sha256 = hashlib.sha256(file_bytes).hexdigest()

        # Build storage key under parent's path
        parent_prefix = parent.storage_key.rsplit("/", 1)[0]
        storage_key = f"{parent_prefix}/{derivative_type}_{file_uuid}.{extension}"

        # Upload to storage
        try:
            from files_management.services.storage_service import StorageService

            client = StorageService._get_client(parent.bucket)
            extra_args = {"ContentType": mime_type}
            if parent.is_public:
                extra_args["ACL"] = "public-read"

            client.put_object(
                Bucket=parent.bucket.spaces_bucket_name,
                Key=storage_key,
                Body=file_bytes,
                **extra_args,
            )
        except Exception as exc:
            logger.error("Derivative upload failed: %s", exc)
            raise

        # Create the derivative record
        derivative = ManagedFile.objects.create(
            uuid=file_uuid,
            website=parent.website,
            site=parent.site,
            bucket=parent.bucket,
            storage_key=storage_key,
            original_filename=f"{derivative_type}_{parent.original_filename}.{extension}",
            file_size_bytes=len(file_bytes),
            mime_type=mime_type,
            file_extension=extension,
            file_kind=parent.file_kind,
            sha256_hash=sha256,
            is_public=parent.is_public,
            parent_file=parent,
            derivative_type=derivative_type,
            lifecycle_status=FileLifecycleStatus.ACTIVE,
            scan_status=FileScanStatus.SKIPPED,  # Derivatives inherit parent's scan
            retention_policy=parent.retention_policy,
            width_px=width,
            height_px=height,
        )

        logger.info(
            "Created %s derivative for %s → %s",
            derivative_type,
            parent.uuid,
            derivative.uuid,
        )
        return derivative