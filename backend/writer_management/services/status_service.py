# writer_management.services.writer_status_service.py

from django.core.cache import cache
from writer_management.models.status import WriterStatus
from writer_management.models.profile import WriterProfile
from writer_management.services.escalation_config_service import EscalationConfigService
from audit_logging.services.audit_log_service import AuditLogService
from writer_management.services.discipline_notification_service import (
    DisciplineNotificationService,
)
class WriterStatusService:
    """
    Service to fetch and update a writer's centralized status,
    cached for fast reads, synced with persistent model.
    """

    @staticmethod
    def get(writer: WriterProfile) -> dict:
        """
        Returns the cached status if available, otherwise updates
        and caches a fresh status.
        """
        cache_key = f"writer_status:{writer.id}"
        status = cache.get(cache_key)
        if status:
            return status

        return WriterStatusService.update(writer)

    @staticmethod
    def update(writer: WriterProfile) -> dict:
        active_strikes = writer.strikes.filter(is_active=True).count()
        is_suspended = writer.suspensions.filter(is_active=True).exists()
        is_blacklisted = writer.blacklist_entries.filter(is_active=True).exists()
        is_on_probation = writer.probation_records.filter(is_active=True).exists()

        last_strike_at = writer.strikes.filter(
            is_active=True
        ).order_by("-created_at").values_list("created_at", flat=True).first()

        suspension_ends_at = writer.suspensions.filter(
            is_active=True
        ).order_by("-ends_at").values_list("ends_at", flat=True).first()

        probation_ends_at = writer.probation_records.filter(
            is_active=True
        ).order_by("-ends_at").values_list("ends_at", flat=True).first()

        is_active = not (is_suspended or is_blacklisted)

        active_warnings = writer.warnings.filter(is_active=True).count()
        config = EscalationConfigService.get_config(writer.website)

        should_suspend = (
            config.auto_suspension_threshold and
            active_warnings >= config.auto_suspension_threshold
        )
        should_probate = (
            config.auto_probation_threshold and
            active_warnings >= config.auto_probation_threshold
        )

        prev = WriterStatusService.get(writer)
        prev_active_strikes = (
            prev.get("active_strikes")
            if isinstance(prev, dict)
            else getattr(prev, "active_strikes", 0)
        ) if prev else 0

        WriterStatus.objects.update_or_create(
            writer=writer,
            defaults={
                "website": writer.website,
                "is_active": is_active,
                "is_suspended": is_suspended,
                "is_blacklisted": is_blacklisted,
                "is_on_probation": is_on_probation,
                "active_strikes": active_strikes,
                "last_strike_at": last_strike_at,
                "suspension_ends_at": suspension_ends_at,
                "probation_ends_at": probation_ends_at,
                "should_be_suspended": should_suspend,
                "should_be_probated": should_probate,
            }
        )

        status = {
            "is_active": is_active,
            "is_suspended": is_suspended,
            "is_blacklisted": is_blacklisted,
            "is_on_probation": is_on_probation,
            "active_strikes": active_strikes,
            "last_strike_at": last_strike_at,
            "suspension_ends_at": suspension_ends_at,
            "probation_ends_at": probation_ends_at,
            "should_be_suspended": should_suspend,
            "should_be_probated": should_probate,
        }

        if (
            config.max_strikes
            and prev
            and prev_active_strikes < config.max_strikes <= active_strikes
        ):
            DisciplineNotificationService.notify_strike_threshold(
                writer,
                strikes=active_strikes,
                threshold=config.max_strikes,
            )

        WriterStatusService._notify_on_change(writer, prev, status)
        cache.set(f"writer_status:{writer.id}", status, timeout=300)

        AuditLogService.log(
            actor=None,  # system-initiated
            target=writer.user,
            action="status_changed",
            message=f"Writer {writer.user.username} status updated.",
            metadata={
                "status": status,
                "warnings": active_warnings,
                "escalation_flags": {
                    "should_be_suspended": should_suspend,
                    "should_be_probated": should_probate
                }
            }
        )

        if should_suspend:
            AuditLogService.log(
                actor=None,
                target=writer.user,
                action="status_auto_flagged",
                message=(
                    f"Writer {writer.user.username} flagged for suspension: "
                    f"{active_warnings} active warnings."
                )
            )
        return status


    @staticmethod
    def clear_cache(writer: WriterProfile) -> None:
        """
        Clears the cached status for a writer.
        """
        cache.delete(f"writer_status:{writer.id}")
    @staticmethod
    def _notify_on_change(writer, prev, new):
        def notify(message):
            from notifications_system.services.dispatch import send
            send(
                user=writer.user,
                title="Account Status Update",
                message=message,
                category="writer_status",
                notification_type="in_app",
                context={"writer_id": writer.id},
                message_type="info"
            )

        if new["is_suspended"] and not prev["is_suspended"]:
            notify("You have been suspended from accessing orders.")

        if not new["is_suspended"] and prev["is_suspended"]:
            notify("Your suspension has been lifted.")

        if new["is_blacklisted"] and not prev["is_blacklisted"]:
            notify("You have been blacklisted and cannot access the platform.")

        if not new["is_blacklisted"] and prev["is_blacklisted"]:
            notify("Your blacklist status has been cleared.")

        if new["is_on_probation"] and not prev["is_on_probation"]:
            notify("You are now on probation. Your account is under review.")

        if not new["is_on_probation"] and prev["is_on_probation"]:
            notify("You are no longer on probation.")

        if new["active_strikes"] > prev["active_strikes"]:
            notify(f"You received a new strike. Total: {new['active_strikes']}.")

        if new["active_strikes"] < prev["active_strikes"]:
            notify(f"A strike was cleared. Total: {new['active_strikes']}.")

        if new["is_active"] and not prev["is_active"]:
            notify("Your account has been re-enabled.")
