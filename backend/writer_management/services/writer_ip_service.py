"""
Records IP addresses used by writers. Used for fraud detection.
"""
import logging
from datetime import date
 
from writer_management.models.logs import WriterIPLog
 
logger = logging.getLogger(__name__)
 
 
class WriterIPService:
 
    @staticmethod
    def record(
        writer,
        ip_address: str,
        user_agent: str = "",
    ) -> WriterIPLog | None:
        """
        Record an IP address for a writer.
 
        Deduplicates: one entry per IP per writer per day.
        If the same IP is seen again today, skips creation.
 
        Args:
            writer:     WriterProfile instance.
            ip_address: IP address string.
            user_agent: Browser user agent string.
 
        Returns:
            WriterIPLog or None (if deduped or error).
        """
        try:
            from writer_management.utils import resolve_website_for_writer
            website = resolve_website_for_writer(writer)
            if website is None:
                return None
 
            today = date.today()
            already_logged = WriterIPLog.objects.filter(
                writer=writer,
                ip_address=ip_address,
                logged_at__date=today,
            ).exists()
 
            if already_logged:
                return None
 
            entry = WriterIPLog.objects.create(
                website=website,
                writer=writer,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            return entry
        except Exception as exc:
            logger.exception(
                "WriterIPService.record failed: writer=%s ip=%s: %s",
                getattr(writer, "registration_id", "?"),
                ip_address,
                exc,
            )
            return None
 
    @staticmethod
    def get_recent_ips(writer, days: int = 30) -> list[str]:
        """Return distinct IPs used by writer in the last N days."""
        from django.utils.timezone import now
        from datetime import timedelta
 
        cutoff = now() - timedelta(days=days)
        return list(
            WriterIPLog.objects.filter(
                writer=writer,
                logged_at__gte=cutoff,
            )
            .values_list("ip_address", flat=True)
            .distinct()
            .order_by("ip_address")
        )
 
    @staticmethod
    def flag_suspicious(writer) -> bool:
        """
        Check if writer shows suspicious IP patterns.
        Currently: more than 3 distinct geographic IPs today.
        Returns True if suspicious.
        """
        today = date.today()
        distinct_today = WriterIPLog.objects.filter(
            writer=writer,
            logged_at__date=today,
        ).values("ip_address").distinct().count()
        return distinct_today > 3