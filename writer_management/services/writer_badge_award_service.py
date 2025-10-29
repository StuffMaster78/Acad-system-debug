from django.utils.timezone import now
from writer_management.models.badges import WriterBadge, Badge
from audit_logging.services import AuditLogService
from writer_management.notification_handlers import send_badge_awarded_notification, send_badge_revoked_notification


class WriterBadgeAwardService:
    """Service for managing writer badge awards and revocations."""
    @staticmethod
    def award_badge(writer, badge: Badge, *, is_auto=True, notes=""):
        """
        Award a badge to a writer.
        :param writer: The writer to award the badge to.
        :param badge: The Badge instance to award.
        :param is_auto: Whether the badge is auto-awarded by the system.
        :param notes: Optional notes for the award.
        :return: The WriterBadge instance if awarded, None if already awarded.
        """
        if WriterBadge.objects.filter(
            writer=writer, badge=badge, revoked=False
        ).exists():
            return None  # Already awarded

        writer_badge = WriterBadge.objects.create(
            writer=writer,
            badge=badge,
            is_auto_awarded=is_auto,
            notes=notes
        )

        # Log
        AuditLogService.log(
            actor=None if is_auto else badge.created_by,
            target=writer.user,
            action="writer_badge.awarded",
            message=f"Badge '{badge.name}' awarded to writer.",
            extra={"badge": badge.name, "auto": is_auto}
        )

        # Send notification
        send_badge_awarded_notification(writer_badge)

        return writer_badge

    @staticmethod
    def revoke_badge(writer_badge: WriterBadge, by_admin, reason=""):
        """
        Revoke a badge from a writer.
        :param writer_badge: The WriterBadge instance to revoke.
        :param by_admin: The admin user performing the revocation.
        :param reason: Reason for revocation.
        :return: True if revoked successfully, False if already revoked.  
        """
        if writer_badge.revoked:
            return False  # Already revoked

        writer_badge.revoked = True
        writer_badge.revoked_at = now()
        writer_badge.revoked_by = by_admin
        writer_badge.revoked_reason = reason
        writer_badge.save()

        # Log
        AuditLogService.log(
            actor=by_admin,
            target=writer_badge.writer.user,
            action="writer_badge.revoked",
            message=f"Badge '{writer_badge.badge.name}' revoked.",
            extra={"reason": reason}
        )

        # Send notification
        send_badge_revoked_notification(writer_badge)

        return True