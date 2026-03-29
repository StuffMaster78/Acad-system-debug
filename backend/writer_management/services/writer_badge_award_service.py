from django.utils.timezone import now

from audit_logging.services.audit_log_service import AuditLogService
from notifications_system.services.notification_service import (
    NotificationService,
)
from writer_management.models.badges import Badge, WriterBadge


class WriterBadgeAwardService:
    """Service for managing writer badge awards and revocations."""

    @staticmethod
    def award_badge(
        writer,
        badge: Badge,
        *,
        is_auto=True,
        notes="",
        awarded_by=None,
    ):
        """
        Award a badge to a writer.

        Args:
            writer: Writer profile receiving the badge.
            badge: Badge instance to award.
            is_auto: Whether the badge is auto-awarded by the system.
            notes: Optional notes for the award.
            awarded_by: User who manually awarded the badge.

        Returns:
            The created WriterBadge instance, or None if already active.
        """
        if WriterBadge.objects.filter(
            writer=writer,
            badge=badge,
            revoked=False,
        ).exists():
            return None

        writer_badge = WriterBadge.objects.create(
            writer=writer,
            badge=badge,
            is_auto_awarded=is_auto,
            notes=notes,
        )

        actor = None if is_auto else awarded_by

        AuditLogService.log(
            actor=actor,
            target=writer.user,
            action="writer_badge.awarded",
            message=f"Badge '{badge.name}' awarded to writer.",
            extra={
                "badge": badge.name,
                "badge_id": badge.id,
                "badge_rule_code": badge.rule_code,
                "auto": is_auto,
            },
        )

        WriterBadgeAwardService._notify_badge_awarded(
            writer_badge=writer_badge,
            triggered_by=actor,
        )

        return writer_badge

    @staticmethod
    def revoke_badge(writer_badge: WriterBadge, by_admin, reason=""):
        """
        Revoke a badge from a writer.

        Args:
            writer_badge: WriterBadge instance to revoke.
            by_admin: Admin user performing the revocation.
            reason: Reason for revocation.

        Returns:
            True if revoked successfully, else False.
        """
        if writer_badge.revoked:
            return False

        writer_badge.revoked = True
        writer_badge.revoked_at = now()
        writer_badge.revoked_by = by_admin
        writer_badge.revoked_reason = reason
        writer_badge.save(
            update_fields=[
                "revoked",
                "revoked_at",
                "revoked_by",
                "revoked_reason",
            ]
        )

        AuditLogService.log(
            actor=by_admin,
            target=writer_badge.writer.user,
            action="writer_badge.revoked",
            message=f"Badge '{writer_badge.badge.name}' revoked.",
            extra={
                "badge": writer_badge.badge.name,
                "badge_id": writer_badge.badge.id,
                "badge_rule_code": writer_badge.badge.rule_code,
                "reason": reason,
            },
        )

        WriterBadgeAwardService._notify_badge_revoked(
            writer_badge=writer_badge,
            triggered_by=by_admin,
            reason=reason,
        )

        return True

    @staticmethod
    def _notify_badge_awarded(
        *,
        writer_badge: WriterBadge,
        triggered_by=None,
    ) -> None:
        """Notify a writer that a badge has been awarded."""
        writer = writer_badge.writer
        badge = writer_badge.badge
        user = getattr(writer, "user", None)
        website = getattr(writer, "website", None)

        if not user or not website:
            return

        NotificationService.notify(
            event_key="writer.badges.awarded",
            recipient=user,
            website=website,
            context={
                "writer_id": writer.id,
                "writer_name": user.get_full_name() or user.username,
                "badge_id": badge.id,
                "badge_name": badge.name,
                "badge_icon": badge.icon,
                "badge_rule_code": badge.rule_code,
                "badge_type": badge.type,
                "is_auto_awarded": writer_badge.is_auto_awarded,
                "notes": writer_badge.notes,
                "issued_at": writer_badge.issued_at.isoformat(),
            },
            triggered_by=triggered_by,
            is_digest=True,
            digest_group="writer_badges",
        )

    @staticmethod
    def _notify_badge_revoked(
        *,
        writer_badge: WriterBadge,
        triggered_by,
        reason="",
    ) -> None:
        """Notify a writer that a badge has been revoked."""
        writer = writer_badge.writer
        badge = writer_badge.badge
        user = getattr(writer, "user", None)
        website = getattr(writer, "website", None)

        if not user or not website:
            return

        NotificationService.notify(
            event_key="writer.badges.revoked",
            recipient=user,
            website=website,
            context={
                "writer_id": writer.id,
                "writer_name": user.get_full_name() or user.username,
                "badge_id": badge.id,
                "badge_name": badge.name,
                "badge_icon": badge.icon,
                "badge_rule_code": badge.rule_code,
                "badge_type": badge.type,
                "revoked_at": (
                    writer_badge.revoked_at.isoformat()
                    if writer_badge.revoked_at
                    else None
                ),
                "revoked_reason": reason,
            },
            triggered_by=triggered_by,
            is_digest=True,
            digest_group="writer_badges",
        )