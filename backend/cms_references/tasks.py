"""
Celery tasks for cms_references.
"""

from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def verify_reference_urls(self):
    """Weekly task: check all references with URLs for link rot."""
    from cms_references.models import Reference
    from cms_references.services.resolvers import LinkRotChecker

    references = Reference.objects.filter(url__gt="").exclude(url="")
    checked = 0
    dead = 0

    for ref in references.iterator(chunk_size=100):
        result = LinkRotChecker.check_url(ref.url)

        ref.last_verified = timezone.now()
        ref.is_url_dead = not result["reachable"]
        ref.save(update_fields=["last_verified", "is_url_dead"])

        checked += 1
        if ref.is_url_dead:
            dead += 1
            logger.warning(
                "Dead URL detected: Reference #%s '%s' — %s",
                ref.id,
                ref.title[:50],
                ref.url,
            )

    logger.info(
        "Link rot check complete: %d checked, %d dead",
        checked,
        dead,
    )
    return {"checked": checked, "dead": dead}


@shared_task(bind=True, max_retries=3)
def archive_reference_url(self, reference_id):
    """Archive a single reference's URL via Wayback Machine.
    Called when a new Reference is created with a URL."""
    from cms_references.models import Reference
    from cms_references.services.resolvers import WaybackArchiver

    try:
        ref = Reference.objects.get(id=reference_id)
    except Reference.DoesNotExist:
        logger.error("Reference #%s not found for archiving", reference_id)
        return

    if not ref.url:
        return

    if ref.url_archived:
        logger.debug("Reference #%s already archived", reference_id)
        return

    archived_url = WaybackArchiver.archive(ref.url)

    if archived_url:
        ref.url_archived = archived_url
        ref.save(update_fields=["url_archived"])
        logger.info(
            "Archived Reference #%s: %s → %s",
            ref.id,
            ref.url,
            archived_url,
        )
    else:
        logger.warning(
            "Failed to archive Reference #%s: %s",
            ref.id,
            ref.url,
        )
        raise self.retry(countdown=300)  # Retry in 5 minutes