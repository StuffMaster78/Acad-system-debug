"""
Creates WriterActionLog entries after discipline events.
Called by DisciplineService after every mutation.
"""
import logging

from writer_management.models.logs import WriterActionLog

logger = logging.getLogger(__name__)


class WriterActionLogService:

    @staticmethod
    def log(
        writer,
        action: str,
        reason: str = "",
        performed_by=None,
        source_object_id: int | None = None,
    ) -> WriterActionLog | None:
        """
        Create a WriterActionLog entry.

        Args:
            writer: WriterProfile instance.
            action: WriterActionLog.ActionType value.
            reason: Reason or notes for the action.
            performed_by: Admin User. None = system.
            source_object_id: PK of the source record (strike PK, etc.).

        Returns:
            WriterActionLog instance or None on failure.
        """
        try:
            from writer_management.utils import resolve_website_for_writer
            website = resolve_website_for_writer(writer)
            if website is None:
                logger.warning(
                    "WriterActionLogService.log: cannot resolve website "
                    "for writer=%s action=%s",
                    writer.registration_id,
                    action,
                )
                return None

            entry = WriterActionLog.objects.create(
                website=website,
                writer=writer,
                action=action,
                reason=reason,
                performed_by=performed_by,
                source_object_id=source_object_id,
            )
            return entry
        except Exception as exc:
            logger.exception(
                "WriterActionLogService.log failed: writer=%s action=%s: %s",
                getattr(writer, "registration_id", "?"),
                action,
                exc,
            )
            return None