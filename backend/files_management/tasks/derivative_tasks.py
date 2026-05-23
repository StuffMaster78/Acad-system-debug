from __future__ import annotations

import logging

from celery import shared_task

from files_management.models.managed_file import ManagedFile

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_derivatives(self, managed_file_id: int) -> None:
    """
    Generate file derivatives such as thumbnails, previews, and optimized
    versions.

    This is intentionally minimal for now. Add Pillow/Willow processing
    after the core upload flow is stable.
    """

    try:
        managed_file = ManagedFile.objects.get(pk=managed_file_id)
    except ManagedFile.DoesNotExist:
        logger.warning(
            "Derivative generation skipped. ManagedFile %s does not exist.",
            managed_file_id,
        )
        return

    try:
        logger.info(
            "Derivative generation placeholder completed for ManagedFile %s.",
            managed_file.pk,
        )

    except Exception as exc:
        logger.exception(
            "Derivative generation failed for ManagedFile %s.",
            managed_file_id,
        )
        raise self.retry(exc=exc) from exc