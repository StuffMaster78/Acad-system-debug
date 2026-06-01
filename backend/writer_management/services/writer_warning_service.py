"""
writer_management/services/writer_warning_service.py

Issues and manages writer warnings.

RESPONSIBILITY
--------------
This service owns the warning lifecycle:
    issue_warning() — create a warning, notify, check thresholds
    revoke_warning() — void a warning issued in error
    void_warning() — alias for revoke_warning (same operation)
    get_active_count() — count active warnings for a writer

ESCALATION
----------
After every new warning, this service evaluates thresholds
from WriterWarningEscalationConfig and calls DisciplineService
for auto-escalation. It does NOT execute the escalation itself —
DisciplineService owns suspension and probation.

After every mutation, this service calls WriterStatusService.recompute()
to rebuild WriterDisciplineState. This keeps the cache consistent.

IDENTITY RESOLUTION
-------------------
WriterProfile has no .user or .website attributes.
All resolution goes through _resolve_website() and _resolve_user()
which navigate the correct chain:
    website → writer.writer_level.website
              or writer.account_profile.website
    user → writer.account_profile.user
"""

import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from writer_management.models.writer_profile import WriterProfile
from writer_management.models.writer_warning import WriterWarning

logger = logging.getLogger(__name__)


class WriterWarningService:

    # ----------------------------------------------------------------
    # ISSUE
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def issue_warning(
        writer: WriterProfile,
        reason: str,
        category: str = "other",
        issued_by=None,
        expires_days: int | None = None,
    ) -> WriterWarning:
        """
        Issue a formal warning to a writer.

        Creates the warning record, notifies the writer,
        evaluates escalation thresholds, rebuilds discipline state.

        Args:
            writer: WriterProfile receiving the warning.
            reason: Full description of the behaviour.
                         Include order number and policy reference.
            category: WriterWarning.category choice value.
            issued_by: Admin User. None = system-triggered.
            expires_days: Override expiry duration in days.
                          Defaults to WriterWarningEscalationConfig value.

        Returns:
            Created WriterWarning instance.

        Raises:
            ValueError: If website cannot be resolved.
        """
        website = WriterWarningService._resolve_website(writer)
        if not website:
            raise ValueError(
                f"Cannot resolve website for writer "
                f"{writer.registration_id}."
            )

        config = WriterWarningService._get_config(website)

        duration = expires_days or getattr(
            config, "default_warning_duration_days", 30
        )
        expires_at = now() + timedelta(days=duration)

        warning = WriterWarning.objects.create(
            website=website,
            writer=writer,
            reason=reason,
            category=category,
            issued_by=issued_by,
            expires_at=expires_at,
        )

        logger.info(
            "WriterWarning issued: writer=%s warning=%s "
            "category=%s expires=%s",
            writer.registration_id,
            warning.pk,
            category,
            expires_at.date(),
        )

        # Rebuild discipline state cache
        WriterWarningService._recompute(writer)

        # Notify writer
        WriterWarningService._notify_writer(
            warning=warning,
            triggered_by=issued_by,
        )

        # Evaluate thresholds and trigger escalation if needed
        WriterWarningService._evaluate_thresholds(
            writer=writer,
            website=website,
            config=config,
        )

        return warning

    # ----------------------------------------------------------------
    # VOID / REVOKE
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def void_warning(
        warning: WriterWarning,
        voided_by=None,
        reason: str = "",
    ) -> WriterWarning:
        """
        Void a warning issued in error.

        Voided warnings are preserved for audit but excluded from
        all threshold counts. The void is permanent.

        Args:
            warning: WriterWarning to void.
            voided_by: Admin User performing the void.
            reason: Why the warning is being voided. Required.

        Returns:
            Updated warning instance.

        Raises:
            ValueError: If reason is not provided.
        """
        if not reason.strip():
            raise ValueError(
                "A reason must be provided when voiding a warning."
            )

        if warning.is_voided:
            logger.warning(
                "void_warning called on already-voided warning %s.",
                warning.pk,
            )
            return warning

        warning.is_voided = True
        warning.is_active = False
        warning.voided_at = now()
        warning.voided_by = voided_by
        warning.void_reason = reason
        warning.save(update_fields=[
            "is_voided", "is_active",
            "voided_at", "voided_by", "void_reason",
            "updated_at",
        ])

        logger.info(
            "WriterWarning voided: warning=%s writer=%s by=%s reason=%r",
            warning.pk,
            warning.writer.pk,
            getattr(voided_by, "pk", "system"),
            reason[:80],
        )

        # Rebuild discipline state — active warning count changes
        WriterWarningService._recompute(warning.writer)

        return warning

    # Alias
    revoke_warning = void_warning

    # ----------------------------------------------------------------
    # QUERIES
    # ----------------------------------------------------------------

    @staticmethod
    def get_active_count(writer: WriterProfile) -> int:
        """
        Count active, non-expired, non-voided warnings for a writer.

        This is the authoritative count used for threshold evaluation.
        WriterDisciplineState.active_warning_count is the cached version.
        """
        return WriterWarning.objects.filter(
            writer=writer,
            is_active=True,
            is_voided=False,
        ).filter(
            Q(expires_at__isnull=True) |
            Q(expires_at__gt=now())
        ).count()

    @staticmethod
    def get_active_warnings(writer: WriterProfile):
        """Return active warning queryset for a writer."""
        n = now()
        return WriterWarning.objects.filter(
            writer=writer,
            is_active=True,
            is_voided=False,
        ).filter(
            Q(expires_at__isnull=True) |
            Q(expires_at__gt=n)
        ).order_by("-created_at")

    # ----------------------------------------------------------------
    # THRESHOLD EVALUATION
    # ----------------------------------------------------------------

    @staticmethod
    def _evaluate_thresholds(writer, website, config) -> None:
        """
        Check if active warning count crosses configured thresholds.
        Trigger notifications and auto-escalation accordingly.
        """
        if config is None:
            return

        current_count = WriterWarningService.get_active_count(writer)

        # Determine highest threshold crossed
        auto_suspension = getattr(config, "auto_suspension_threshold", 0)
        auto_probation = getattr(config, "auto_probation_threshold", 0)
        admin_alert = getattr(config, "admin_alert_threshold", 0)

        # Auto-suspension (highest priority)
        if auto_suspension and current_count >= auto_suspension:
            logger.warning(
                "Auto-suspension threshold reached: writer=%s "
                "active_warnings=%d threshold=%d",
                writer.registration_id,
                current_count,
                auto_suspension,
            )
            WriterWarningService._trigger_suspension(writer, config)
            WriterWarningService._notify_admins(
                writer=writer,
                website=website,
                current_count=current_count,
                suggested_action="suspension_triggered",
                config=config,
            )
            return

        # Auto-probation
        if auto_probation and current_count >= auto_probation:
            logger.info(
                "Auto-probation threshold reached: writer=%s "
                "active_warnings=%d threshold=%d",
                writer.registration_id,
                current_count,
                auto_probation,
            )
            WriterWarningService._trigger_probation(writer, config)
            WriterWarningService._notify_admins(
                writer=writer,
                website=website,
                current_count=current_count,
                suggested_action="probation_triggered",
                config=config,
            )
            return

        # Admin alert only
        if admin_alert and current_count >= admin_alert:
            logger.info(
                "Admin alert threshold reached: writer=%s "
                "active_warnings=%d threshold=%d",
                writer.registration_id,
                current_count,
                admin_alert,
            )
            WriterWarningService._notify_admins(
                writer=writer,
                website=website,
                current_count=current_count,
                suggested_action="review_recommended",
                config=config,
            )

    @staticmethod
    def _trigger_suspension(writer, config) -> None:
        """Auto-suspend via DisciplineService."""
        try:
            from writer_management.services.discipline_service import (
                DisciplineService,
            )
            from writer_management.exceptions import WriterSuspendedError

            DisciplineService.suspend(
                writer=writer,
                reason=(
                    f"Auto-suspended: active warning count reached "
                    f"suspension threshold "
                    f"({config.auto_suspension_threshold} warnings)."
                ),
                duration_days=getattr(config, "auto_suspend_days", 7),
                auto_triggered=True,
            )
        except Exception as exc:
            logger.exception(
                "Auto-suspension failed for writer %s: %s",
                writer.registration_id,
                exc,
            )

    @staticmethod
    def _trigger_probation(writer, config) -> None:
        """Auto-probation via DisciplineService."""
        try:
            from writer_management.services.discipline_service import (
                DisciplineService,
            )

            DisciplineService.place_on_probation(
                writer=writer,
                reason=(
                    f"Auto-probation: active warning count reached "
                    f"probation threshold "
                    f"({config.auto_probation_threshold} warnings)."
                ),
                auto_triggered=True,
            )
        except Exception as exc:
            logger.exception(
                "Auto-probation failed for writer %s: %s",
                writer.registration_id,
                exc,
            )

    # ----------------------------------------------------------------
    # NOTIFICATIONS
    # ----------------------------------------------------------------

    @staticmethod
    def _notify_writer(warning: WriterWarning, triggered_by=None) -> None:
        """Notify writer that a warning was issued."""
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            writer = warning.writer
            user = WriterWarningService._resolve_user(writer)
            if not user:
                logger.warning(
                    "Cannot notify writer %s — user not resolvable.",
                    writer.registration_id,
                )
                return

            NotificationService.notify(
                event_key="writer.discipline.warning_issued",
                recipient=user,
                website=warning.website,
                context={
                    "registration_id": writer.registration_id,
                    "warning_id": warning.pk,
                    "category": warning.category,
                    "reason": warning.reason,
                    "issued_at": warning.created_at.isoformat(),
                    "expires_at": (
                        warning.expires_at.isoformat()
                        if warning.expires_at else None
                    ),
                    "active_warning_count": (
                        WriterWarningService.get_active_count(writer)
                    ),
                    "days_remaining": warning.days_remaining,
                },
                triggered_by=triggered_by,
            )
        except Exception as exc:
            logger.exception(
                "Warning notification failed for warning %s: %s",
                warning.pk,
                exc,
            )

    @staticmethod
    def _notify_admins(
        *,
        writer,
        website,
        current_count: int,
        suggested_action: str,
        config,
    ) -> None:
        """Notify admin users when a threshold is crossed."""
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            admin_users = WriterWarningService._get_admin_recipients(website)

            for admin in admin_users:
                NotificationService.notify(
                    event_key="writer.discipline.warning_threshold_reached",
                    recipient=admin,
                    website=website,
                    context={
                        "registration_id": writer.registration_id,
                        "active_warning_count": current_count,
                        "suggested_action": suggested_action,
                        "admin_alert_threshold": config.admin_alert_threshold,
                    },
                    triggered_by=None,
                    is_critical=True,
                )
        except Exception as exc:
            logger.exception(
                "Admin threshold notification failed for writer %s: %s",
                writer.registration_id,
                exc,
            )

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _recompute(writer) -> None:
        """Rebuild WriterDisciplineState after any warning mutation."""
        try:
            from writer_management.services.writer_status_service import (
                WriterStatusService,
            )
            WriterStatusService.recompute(writer)
        except Exception as exc:
            logger.exception(
                "Failed to recompute discipline state for writer %s: %s",
                writer.registration_id,
                exc,
            )

    @staticmethod
    def _get_config(website):
        """Get WriterWarningEscalationConfig for a website."""
        from writer_management.models.configs import (
            WriterWarningEscalationConfig,
        )
        try:
            return WriterWarningEscalationConfig.objects.get(website=website)
        except WriterWarningEscalationConfig.DoesNotExist:
            logger.warning(
                "No WriterWarningEscalationConfig for website %s.",
                website.pk,
            )
            return None

    @staticmethod
    def _resolve_website(writer):
        try:
            if writer.writer_level_id:
                return writer.writer_level.website
        except Exception:
            pass
        try:
            return writer.account_profile.website
        except Exception:
            return None

    @staticmethod
    def _resolve_user(writer):
        try:
            return writer.account_profile.user
        except Exception:
            return None

    @staticmethod
    def _get_admin_recipients(website):
        from accounts.models.account_profile import AccountProfile
        return (
            AccountProfile.objects
            .filter(
                website=website,
                role__in=["admin", "superadmin"],
                user__is_active=True,
            )
            .select_related("user")
            .values_list("user", flat=True)
        )