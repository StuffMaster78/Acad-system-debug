from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from django.utils import timezone

from notifications_system.enums import NotificationType
from notifications_system.services.dispatch import send


@dataclass
class _NotificationContext:
    writer_id: int
    website_id: Optional[int] = None
    meta: Optional[dict] = None


class DisciplineNotificationService:
    """
    Central place for dispatching writer discipline notifications so that
    warnings, strikes, suspensions, and probation events stay consistent.
    """

    @staticmethod
    def _send(writer, *, event: str, title: str, message: str, context: Optional[dict] = None):
        if not writer or not writer.user:
            return

        payload = {
            "writer_id": writer.id,
            "website_id": getattr(writer, "website_id", None),
        }
        if context:
            payload.update(context)

        send(
            user=writer.user,
            event=event,
            payload=payload,
            website=getattr(writer, "website", None),
            channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET],
            category="writer_discipline",
        )

    # Warning notifications -------------------------------------------------
    @staticmethod
    def notify_warning_issued(warning):
        DisciplineNotificationService._send(
            warning.writer,
            event="discipline.warning.issued",
            title="Warning Issued",
            message=warning.reason,
            context={
                "warning_id": warning.id,
                "warning_type": getattr(warning, "warning_type", "warning"),
                "expires_at": warning.expires_at.isoformat() if warning.expires_at else None,
            },
        )

    @staticmethod
    def notify_warning_resolved(warning, *, reason: str = "resolved"):
        DisciplineNotificationService._send(
            warning.writer,
            event="discipline.warning.resolved",
            title="Warning Updated",
            message=f"A warning has been {reason}. Keep up the great work.",
            context={"warning_id": warning.id, "resolution_reason": reason},
        )

    # Strike notifications --------------------------------------------------
    @staticmethod
    def notify_strike_issued(strike):
        DisciplineNotificationService._send(
            strike.writer,
            event="discipline.strike.issued",
            title="Strike Recorded",
            message=strike.reason,
            context={
                "strike_id": strike.id,
                "issued_at": strike.issued_at.isoformat(),
                "issued_by": getattr(strike.issued_by, "id", None),
            },
        )

    @staticmethod
    def notify_strike_revoked(strike):
        DisciplineNotificationService._send(
            strike.writer,
            event="discipline.strike.revoked",
            title="Strike Removed",
            message="An administrator removed one of your strikes.",
            context={"strike_id": strike.id},
        )

    @staticmethod
    def notify_strike_threshold(writer, *, strikes: int, threshold: int):
        DisciplineNotificationService._send(
            writer,
            event="discipline.strike.threshold",
            title="Strike Threshold Reached",
            message=f"You now have {strikes} active strikes (limit {threshold}). Expect additional reviews.",
            context={"active_strikes": strikes, "threshold": threshold},
        )

    @staticmethod
    def notify_warning_threshold(writer, *, warnings: int, threshold: int):
        DisciplineNotificationService._send(
            writer,
            event="discipline.warning.threshold",
            title="Warning Threshold Reached",
            message=f"You have {warnings} active warnings. Further issues may escalate to suspension.",
            context={"active_warnings": warnings, "threshold": threshold},
        )

    # Suspension notifications ---------------------------------------------
    @staticmethod
    def notify_suspension_started(suspension):
        end_label = (
            f" until {suspension.end_date.strftime('%b %d, %Y %H:%M %Z')}"
            if suspension.end_date
            else ""
        )
        DisciplineNotificationService._send(
            suspension.writer,
            event="discipline.suspension.started",
            title="Account Suspended",
            message=f"Your account is suspended{end_label}. Reason: {suspension.reason}",
            context={
                "suspension_id": suspension.id,
                "end_date": suspension.end_date.isoformat() if suspension.end_date else None,
            },
        )

    @staticmethod
    def notify_suspension_lifted(suspension):
        DisciplineNotificationService._send(
            suspension.writer,
            event="discipline.suspension.ended",
            title="Suspension Lifted",
            message="Your suspension has been lifted. You may resume work.",
            context={"suspension_id": suspension.id},
        )

    # Probation notifications ----------------------------------------------
    @staticmethod
    def notify_probation_started(probation):
        DisciplineNotificationService._send(
            probation.writer,
            event="discipline.probation.started",
            title="You are on Probation",
            message=f"You were placed on probation until {probation.end_date.strftime('%b %d, %Y')}. Reason: {probation.reason}",
            context={"probation_id": probation.id, "end_date": probation.end_date.isoformat()},
        )

    @staticmethod
    def notify_probation_expiring(probation, *, eta: timedelta):
        days_left = max(1, eta.days or 0)
        DisciplineNotificationService._send(
            probation.writer,
            event="discipline.probation.expiring",
            title="Probation Ending Soon",
            message=f"Probation ends in {days_left} day{'s' if days_left != 1 else ''}. Stay compliant to finish with a clean record.",
            context={"probation_id": probation.id, "eta_days": days_left},
        )

    @staticmethod
    def notify_probation_completed(probation):
        DisciplineNotificationService._send(
            probation.writer,
            event="discipline.probation.completed",
            title="Probation Completed",
            message="Great news! Your probation period has ended.",
            context={"probation_id": probation.id},
        )


