"""
Records writer activity events and updates WriterActivityTracking.
"""

from writer_management.models.logs import WriterActivityLog, WriterActivityTracking


class WriterActivityService:

    @staticmethod
    def log_action(
        writer,
        action_type: str,
        description: str = "",
        metadata: dict | None = None,
        ip_address: str | None = None,
    ) -> WriterActivityLog | None:
        """
        Create a WriterActivityLog entry.

        Args:
            writer: WriterProfile instance.
            action_type: WriterActivityLog.ActionType value.
            description: Optional detail.
            metadata: Optional structured context dict.
            ip_address: Optional IP address of the request.

        Returns:
            WriterActivityLog or None on failure.
        """
        try:
            from writer_management.utils import resolve_website_for_writer
            website = resolve_website_for_writer(writer)
            if website is None:
                return None

            return WriterActivityLog.objects.create(
                website=website,
                writer=writer,
                action_type=action_type,
                description=description,
                metadata=metadata or {},
                ip_address=ip_address,
            )
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception(
                "WriterActivityService.log_action failed: writer=%s: %s",
                getattr(writer, "registration_id", "?"),
                exc,
            )
            return None

    @staticmethod
    def record_login(writer, ip_address: str | None = None) -> None:
        """Update WriterActivityTracking on login."""
        try:
            tracking, _ = WriterActivityTracking.objects.get_or_create(
                writer=writer,
                defaults={
                    "website": _resolve_website(writer),
                },
            )
            tracking.update_last_login()
        except Exception:
            pass

        WriterActivityService.log_action(
            writer=writer,
            action_type=WriterActivityLog.ActionType.LOGIN,
            ip_address=ip_address,
        )

    @staticmethod
    def record_heartbeat(writer, ip_address: str | None = None) -> None:
        """Update last_seen on heartbeat ping."""
        try:
            tracking = WriterActivityTracking.objects.get(writer=writer)
            tracking.update_last_seen()
        except WriterActivityTracking.DoesNotExist:
            pass

        # Also update WriterStatus
        try:
            writer.status.record_heartbeat()
        except Exception:
            pass


def _resolve_website(writer):
    from writer_management.utils import resolve_website_for_writer
    return resolve_website_for_writer(writer)