"""
writer_management/services/discipline_notification_service.py

Resolves recipients and builds context for discipline notifications.
Delegates all delivery to notifications_system.NotificationService.

RESPONSIBILITY
--------------
This service knows:
    - Which event_key maps to which discipline event
    - How to resolve a User from a WriterProfile
    - What context variables each discipline template needs

This service does NOT know:
    - How to render templates
    - Which channels to use (email, in-app, SMS)
    - How to queue or deliver messages

All of that is notifications_system's responsibility.

TEMPLATE OWNERSHIP
------------------
Every event_key below must have a corresponding template in
notifications_system. The context dict defines the variables
available to that template.

EVENT KEYS REGISTERED HERE
---------------------------
writer.discipline.warning_issued
writer.discipline.warning_voided
writer.discipline.warning_threshold_reached
writer.discipline.strike_issued
writer.discipline.strike_voided
writer.discipline.suspended
writer.discipline.suspension_lifted
writer.discipline.blacklisted
writer.discipline.blacklist_lifted
writer.discipline.probation_placed
writer.discipline.probation_ended
writer.discipline.penalty_applied

IDENTITY RESOLUTION
-------------------
WriterProfile has no .user attribute.
Resolution: writer.account_profile.user
All notify_* methods resolve this internally.
"""

import logging

from writer_management.models.writer_profile import WriterProfile

logger = logging.getLogger(__name__)


class DisciplineNotificationService:
    """
    Builds and dispatches discipline notifications.

    All methods are static. Call directly:
        DisciplineNotificationService.notify_warning_issued(warning)
    """
    @staticmethod
    def _resolve_website(writer: WriterProfile):
        """
        Resolve website from WriterProfile.
        Tries writer_level first, then account_profile.
        Returns None if neither is available.
        """
        # writer_level is nullable — guard before accessing .website
        if writer.writer_level is not None:
            try:
                return writer.writer_level.website
            except Exception:
                pass

        try:
            return writer.account_profile.website
        except Exception:
            pass

        logger.warning(
            "DisciplineNotificationService: cannot resolve website "
            "for writer=%s",
            writer.registration_id,
        )
        return None

    # ----------------------------------------------------------------
    # WARNINGS
    # ----------------------------------------------------------------

    @staticmethod
    def notify_warning_issued(warning, triggered_by=None) -> None:
        """
        Notify writer that a warning was issued against them.

        Template variables:
            registration_id     — writer's stable ID
            category            — warning category (human readable)
            reason              — full reason text
            issued_at           — ISO timestamp
            expires_at          — ISO timestamp or null
            days_remaining      — int or null
            active_warning_count — current active warning count
        """
        writer = warning.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        from writer_management.services.writer_warning_service import (
            WriterWarningService,
        )

        DisciplineNotificationService._notify(
            event_key="writer.discipline.warning_issued",
            recipient=user,
            website=warning.website,
            context={
                "registration_id":     writer.registration_id,
                "category":            warning.get_category_display(),
                "reason":              warning.reason,
                "issued_at":           warning.created_at.isoformat(),
                "expires_at":          (
                    warning.expires_at.isoformat()
                    if warning.expires_at else None
                ),
                "days_remaining":      warning.days_remaining,
                "active_warning_count": WriterWarningService.get_active_count(writer),
            },
            triggered_by=triggered_by,
        )

    @staticmethod
    def notify_warning_voided(warning, voided_by=None) -> None:
        """
        Notify writer that a warning against them was voided.

        Template variables:
            registration_id — writer's stable ID
            category        — warning category
            void_reason     — why it was voided
            voided_at       — ISO timestamp
        """
        writer = warning.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.warning_voided",
            recipient=user,
            website=warning.website,
            context={
                "registration_id": writer.registration_id,
                "category":        warning.get_category_display(),
                "void_reason":     warning.void_reason,
                "voided_at":       warning.voided_at.isoformat() if warning.voided_at else None,
            },
            triggered_by=voided_by,
        )

    @staticmethod
    def notify_warning_threshold_reached(
        writer: WriterProfile,
        website,
        active_warning_count: int,
        suggested_action: str,
        admin_alert_threshold: int,
        triggered_by=None,
    ) -> None:
        """
        Notify admins that a writer has crossed the warning threshold.

        Sent to ALL admin users on the website.
        Template variables:
            registration_id      — writer's stable ID
            active_warning_count — current count
            threshold            — the threshold crossed
            suggested_action     — what the system recommends
        """
        admins = DisciplineNotificationService._get_admin_recipients(website)

        for admin in admins:
            DisciplineNotificationService._notify(
                event_key="writer.discipline.warning_threshold_reached",
                recipient=admin,
                website=website,
                context={
                    "registration_id":      writer.registration_id,
                    "active_warning_count": active_warning_count,
                    "threshold":            admin_alert_threshold,
                    "suggested_action":     suggested_action,
                },
                triggered_by=triggered_by,
                is_critical=True,
            )

    # ----------------------------------------------------------------
    # STRIKES
    # ----------------------------------------------------------------

    @staticmethod
    def notify_strike_issued(strike, triggered_by=None) -> None:
        """
        Notify writer that a strike was recorded against them.

        Template variables:
            registration_id — writer's stable ID
            category        — strike category (human readable)
            reason          — public-facing reason
            issued_at       — ISO timestamp
        Note:
            evidence_notes is NOT included — internal only.
        """
        writer = strike.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.strike_issued",
            recipient=user,
            website=strike.website,
            context={
                "registration_id": writer.registration_id,
                "category":        strike.get_category_display(),
                "reason":          strike.reason,
                "issued_at":       strike.issued_at.isoformat(),
            },
            triggered_by=triggered_by,
        )

    @staticmethod
    def notify_strike_voided(strike, voided_by=None) -> None:
        """
        Notify writer that a strike against them was voided.

        Template variables:
            registration_id — writer's stable ID
            category        — strike category
            void_reason     — why it was voided
        """
        writer = strike.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.strike_voided",
            recipient=user,
            website=strike.website,
            context={
                "registration_id": writer.registration_id,
                "category":        strike.get_category_display(),
                "void_reason":     strike.void_reason,
            },
            triggered_by=voided_by,
        )

    # ----------------------------------------------------------------
    # SUSPENSION
    # ----------------------------------------------------------------

    @staticmethod
    def notify_suspended(suspension, triggered_by=None) -> None:
        """
        Notify writer they have been suspended.

        Template variables:
            registration_id — writer's stable ID
            reason          — why they were suspended
            end_date        — ISO date or null (null = indefinite)
            auto_triggered  — bool (system vs admin)
            duration_days   — int or null
        """
        writer = suspension.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        duration_days = None
        if suspension.end_date and suspension.start_date:
            delta = suspension.end_date - suspension.start_date
            duration_days = delta.days

        DisciplineNotificationService._notify(
            event_key="writer.discipline.suspended",
            recipient=user,
            website=suspension.website,
            context={
                "registration_id": writer.registration_id,
                "reason":          suspension.reason,
                "end_date":        (
                    suspension.end_date.isoformat()
                    if suspension.end_date else None
                ),
                "auto_triggered":  suspension.auto_triggered,
                "duration_days":   duration_days,
            },
            triggered_by=triggered_by,
        )

    @staticmethod
    def notify_suspension_lifted(suspension, lifted_by=None) -> None:
        """
        Notify writer their suspension has been lifted.

        Template variables:
            registration_id — writer's stable ID
            lift_reason     — why the suspension was lifted
            lifted_at       — ISO timestamp
        """
        writer = suspension.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.suspension_lifted",
            recipient=user,
            website=suspension.website,
            context={
                "registration_id": writer.registration_id,
                "lift_reason":     suspension.lift_reason,
                "lifted_at":       (
                    suspension.lifted_at.isoformat()
                    if suspension.lifted_at else None
                ),
            },
            triggered_by=lifted_by,
        )

    # ----------------------------------------------------------------
    # BLACKLIST
    # ----------------------------------------------------------------

    @staticmethod
    def notify_blacklisted(blacklist_entry, triggered_by=None) -> None:
        """
        Notify writer they have been blacklisted.

        Template variables:
            registration_id — writer's stable ID
            reason          — why they were blacklisted
            auto_triggered  — bool
        Note:
            Blacklisting is severe. Template should reflect gravity.
        """
        writer = blacklist_entry.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.blacklisted",
            recipient=user,
            website=blacklist_entry.website,
            context={
                "registration_id": writer.registration_id,
                "reason":          blacklist_entry.reason,
                "auto_triggered":  blacklist_entry.auto_triggered,
            },
            triggered_by=triggered_by,
            is_critical=True,
        )

    @staticmethod
    def notify_blacklist_lifted(blacklist_entry, lifted_by=None) -> None:
        """
        Notify writer their blacklist has been lifted.

        Template variables:
            registration_id — writer's stable ID
            lift_reason     — why the blacklist was lifted
        """
        writer = blacklist_entry.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.blacklist_lifted",
            recipient=user,
            website=blacklist_entry.website,
            context={
                "registration_id": writer.registration_id,
                "lift_reason":     blacklist_entry.lift_reason,
            },
            triggered_by=lifted_by,
        )

    # ----------------------------------------------------------------
    # PROBATION
    # ----------------------------------------------------------------

    @staticmethod
    def notify_probation_placed(probation, triggered_by=None) -> None:
        """
        Notify writer they have been placed on probation.

        Template variables:
            registration_id — writer's stable ID
            reason          — why they are on probation
            end_date        — ISO date
            auto_triggered  — bool
        """
        writer = probation.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.probation_placed",
            recipient=user,
            website=probation.website,
            context={
                "registration_id": writer.registration_id,
                "reason":          probation.reason,
                "end_date":        probation.end_date.isoformat(),
                "auto_triggered":  probation.auto_triggered,
            },
            triggered_by=triggered_by,
        )

    @staticmethod
    def notify_probation_ended(probation, ended_by=None) -> None:
        """
        Notify writer their probation has ended.

        Template variables:
            registration_id — writer's stable ID
            ended_at        — ISO timestamp
        """
        writer = probation.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.probation_ended",
            recipient=user,
            website=probation.website,
            context={
                "registration_id": writer.registration_id,
                "ended_at":        (
                    probation.ended_at.isoformat()
                    if probation.ended_at else None
                ),
            },
            triggered_by=ended_by,
        )

    # ----------------------------------------------------------------
    # PENALTY
    # ----------------------------------------------------------------

    @staticmethod
    def notify_penalty_applied(penalty, triggered_by=None) -> None:
        """
        Notify writer a financial penalty was applied.

        Template variables:
            registration_id — writer's stable ID
            reason          — penalty reason (human readable)
            amount_deducted — formatted decimal string
            order_id        — order PK or null
            notes           — additional context (if not empty)
        """
        writer = penalty.writer
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            return

        DisciplineNotificationService._notify(
            event_key="writer.discipline.penalty_applied",
            recipient=user,
            website=penalty.website,
            context={
                "registration_id": writer.registration_id,
                "reason":          penalty.get_reason_display(),
                "amount_deducted": str(penalty.amount_deducted),
                "order_id":        penalty.order_id,
                "notes":           penalty.notes or None,
            },
            triggered_by=triggered_by,
        )

    # ----------------------------------------------------------------
    # GENERIC NOTIFY — wraps NotificationService
    # ----------------------------------------------------------------

    @staticmethod
    def notify(
        event_key: str,
        writer: WriterProfile,
        context: dict,
        triggered_by=None,
        is_critical: bool = False,
    ) -> None:
        """
        Generic discipline notification.

        Resolves the writer's User and website, then delegates
        to NotificationService.
        """
        user = DisciplineNotificationService._resolve_user(writer)
        if not user:
            logger.warning(
                "DisciplineNotificationService.notify: "
                "cannot resolve user for writer=%s event=%s",
                writer.registration_id,
                event_key,
            )
            return

        website = DisciplineNotificationService._resolve_website(writer)
        if not website:
            logger.warning(
                "DisciplineNotificationService.notify: "
                "cannot resolve website for writer=%s event=%s",
                writer.registration_id,
                event_key,
            )
            return

        DisciplineNotificationService._notify(
            event_key=event_key,
            recipient=user,
            website=website,
            context={
                "registration_id": writer.registration_id,
                **context,
            },
            triggered_by=triggered_by,
            is_critical=is_critical,
        )

    # ----------------------------------------------------------------
    # INTERNAL DELIVERY
    # ----------------------------------------------------------------

    @staticmethod
    def _notify(
        event_key: str,
        recipient,
        website,
        context: dict,
        triggered_by=None,
        is_critical: bool = False,
    ) -> None:
        """
        Deliver a notification via NotificationService.

        Exceptions are caught and logged — a notification failure
        must never roll back a discipline action.
        """
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context=context,
                triggered_by=triggered_by,
                is_critical=is_critical,
            )
        except Exception as exc:
            logger.exception(
                "DisciplineNotificationService._notify failed: "
                "event=%s recipient=%s: %s",
                event_key,
                getattr(recipient, "pk", "?"),
                exc,
            )

    # ----------------------------------------------------------------
    # IDENTITY RESOLUTION
    # ----------------------------------------------------------------

    @staticmethod
    def _resolve_user(writer: WriterProfile):
        """
        Resolve auth User from WriterProfile.
        Chain: WriterProfile → AccountProfile → User.
        Returns None and logs warning if resolution fails.
        """
        try:
            return writer.account_profile.user
        except Exception:
            logger.warning(
                "DisciplineNotificationService: cannot resolve user "
                "for writer=%s",
                writer.registration_id,
            )
            return None

    @staticmethod
    def _get_admin_recipients(website) -> list:
        """
        Resolve admin users for a website via AccountProfile.
        Returns a list of User instances.
        """
        try:
            from accounts.models.account_profile import AccountProfile
            return list(
                AccountProfile.objects.filter(
                    website=website,
                    role__in=["admin", "superadmin"],
                    user__is_active=True,
                )
                .select_related("user")
                .values_list("user", flat=True)
            )
        except Exception as exc:
            logger.exception(
                "DisciplineNotificationService: failed to resolve "
                "admin recipients for website=%s: %s",
                getattr(website, "pk", "?"),
                exc,
            )
            return []