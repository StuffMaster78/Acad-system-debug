"""
Manages WriterResource views and downloads.
"""
import logging

from django.db import models

from writer_management.models.resources import (
    WriterResource,
    WriterResourceView,
)

logger = logging.getLogger(__name__)


class ResourceService:

    @staticmethod
    def record_view(writer, resource: WriterResource) -> None:
        """
        Record that a writer viewed a resource.

        Upserts WriterResourceView (one per writer per resource).
        Increments view_count on both the view record and the resource.
        """
        try:
            view, created = WriterResourceView.objects.get_or_create(
                resource=resource,
                writer=writer,
                defaults={"view_count": 1},
            )
            if not created:
                WriterResourceView.objects.filter(pk=view.pk).update(
                    view_count=models.F("view_count") + 1
                )

            WriterResource.objects.filter(pk=resource.pk).update(
                view_count=models.F("view_count") + 1
            )
        except Exception as exc:
            logger.exception(
                "ResourceService.record_view failed: resource=%s writer=%s: %s",
                resource.pk,
                getattr(writer, "registration_id", "?"),
                exc,
            )

    @staticmethod
    def record_download(writer, resource: WriterResource) -> None:
        """
        Record that a writer downloaded a resource.

        Increments download_count on the resource.
        Creates a WriterFileDownloadLog entry.

        file_id in the log is the files_management app PK stored on
        WriterResource.files_app_file_id. When not yet set (resource
        predates files app integration), logs with file_id=0 as a
        sentinel so the row is queryable but visibly incomplete.
        """
        try:
            WriterResource.objects.filter(pk=resource.pk).update(
                download_count=models.F("download_count") + 1
            )

            from writer_management.models.logs import WriterFileDownloadLog
            from writer_management.utils import resolve_website_for_writer

            website = resolve_website_for_writer(writer)
            if not website:
                return

            file_id = resource.files_app_file_id # consistent name
            if file_id is None:
                logger.warning(
                    "record_download: resource=%s has no files_app_file_id. "
                    "Log entry created with file_id=0 sentinel.",
                    resource.pk,
                )

            WriterFileDownloadLog.objects.create(
                website=website,
                writer=writer,
                file_id=file_id or 0, # 0 = sentinel for missing files app PK
                file_name=resource.title,
            )

        except Exception as exc:
            logger.exception(
                "ResourceService.record_download failed: resource=%s writer=%s: %s",
                resource.pk,
                getattr(writer, "registration_id", "?"),
                exc,
            )

    @staticmethod
    def get_active_resources(website, category=None):
        """Return active resources for a website, optionally by category."""
        qs = WriterResource.objects.filter(
            website=website,
            is_active=True,
        ).select_related("category").order_by("display_order", "-created_at")
        if category is not None:
            qs = qs.filter(category=category)
        return qs