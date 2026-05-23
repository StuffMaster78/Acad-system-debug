"""
Derivative generation tasks.
Triggered per-file on upload by StorageService.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def generate_derivatives(self, managed_file_id: int):
    """
    Generate thumbnails, WebP, and PDF previews for a file.

    Called after upload.  Skips if not an image or PDF.
    """
    from files_management.models import ManagedFile
    from files_management.services.derivative_service import DerivativeService

    try:
        managed_file = ManagedFile.objects.get(pk=managed_file_id)
    except ManagedFile.DoesNotExist:
        logger.error("Derivative task: ManagedFile %s not found", managed_file_id)
        return {"error": "File not found"}

    mime = managed_file.mime_type or ""
    if not (mime.startswith("image/") or mime == "application/pdf"):
        logger.debug(
            "Skipping derivatives for %s — mime: %s",
            managed_file.uuid,
            mime,
        )
        return {"file_id": managed_file_id, "derivatives": 0, "skipped": True}

    try:
        derivatives = DerivativeService.generate_all(managed_file)
        return {
            "file_id": managed_file_id,
            "uuid": str(managed_file.uuid),
            "derivatives": len(derivatives),
            "types": [d.derivative_type for d in derivatives],
        }
    except Exception as exc:
        logger.error(
            "Derivative generation failed for %s: %s",
            managed_file.uuid,
            exc,
        )
        raise self.retry(exc=exc)


@shared_task
def generate_single_derivative(managed_file_id: int, derivative_type: str):
    """
    Generate a specific derivative type for a file.

    Useful for manual regeneration after a bug fix or format change.
    """
    from files_management.models import ManagedFile
    from files_management.services.derivative_service import (
        DerivativeService,
        THUMBNAIL_SIZES,
    )

    try:
        managed_file = ManagedFile.objects.get(pk=managed_file_id)
    except ManagedFile.DoesNotExist:
        return {"error": "File not found"}

    if derivative_type in THUMBNAIL_SIZES:
        size = THUMBNAIL_SIZES[derivative_type]
        deriv = DerivativeService._generate_image_thumbnail(
            managed_file, derivative_type, size
        )
    elif derivative_type == "webp":
        deriv = DerivativeService._generate_webp(managed_file)
    elif derivative_type == "preview_pdf":
        deriv = DerivativeService._generate_pdf_preview(managed_file)
    else:
        return {"error": f"Unknown derivative type: {derivative_type}"}

    return {
        "file_id": managed_file_id,
        "derivative_type": derivative_type,
        "created": deriv is not None,
    }
