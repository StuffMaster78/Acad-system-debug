# writer_management/services/writer_warning_service.py

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from notifications_system.services.notification_service import (
    NotificationService,
)
from writer_management.models.profile import WriterProfile
from writer_management.models.writer_warnings import WriterWarning
from writer_management.services.escalation_config_service import (
    EscalationConfigService,
)

User = get_user_model()


class WriterWarningService:
    """Service for issuing writer warnings and handling thresholds."""

    @staticmethod
    def issue_warning(
        writer: WriterProfile,
        reason: str,
        issued_by=None,
        expires_days: int | None = None,
    ) -> WriterWarning:
        """
        Issue a warning to a writer and trigger relevant notifications.

        Args:
            writer: Writer profile receiving the warning.
            reason: Reason for the warning.
            issued_by: User who issued the warning, or None for system.
            expires_days: Optional override for warning expiration days.

        Returns:
            The created WriterWarning instance.
        """
        website = getattr(writer, "website", None)
        if not website:
            raise ValueError("Writer must belong to a website.")

        config = EscalationConfigService.get_config(website)
        previous_count = WriterWarningService.get_active_warning_count(writer)

        expires_days = (
            expires_days or config.default_warning_duration_days
        )
        expires_at = now() + timedelta(days=expires_days)

        warning = WriterWarning.objects.create(
            website=website,
            writer=writer,
            reason=reason,
            issued_by=issued_by,
            expires_at=expires_at,
        )

        WriterWarningService._notify_warning_issued(
            warning=warning,
            triggered_by=issued_by,
        )

        WriterWarningService.check_threshold(
            writer=writer,
            previous_count=previous_count,
        )

        return warning

    @staticmethod
    def get_active_warning_count(writer: WriterProfile) -> int:
        """
        Return the number of active, unexpired warnings for a writer.

        Args:
            writer: Writer profile to evaluate.

        Returns:
            Number of active warnings.
        """
        return writer.warnings.filter(
            is_active=True,
            expires_at__gt=now(),
        ).count()

    @staticmethod
    def check_threshold(
        writer: WriterProfile,
        previous_count: int | None = None,
    ) -> None:
        """
        Notify admins if the writer crosses the configured threshold.

        Args:
            writer: Writer profile to evaluate.
            previous_count: Warning count before latest change.
        """
        website = getattr(writer, "website", None)
        if not website:
            return

        config = EscalationConfigService.get_config(website)
        current_count = WriterWarningService.get_active_warning_count(
            writer
        )

        if previous_count is None:
            previous_count = current_count

        crossed_threshold = (
            previous_count < config.admin_alert_threshold
            <= current_count
        )

        if crossed_threshold:
            WriterWarningService._notify_warning_threshold(
                writer=writer,
                warnings=current_count,
                threshold=config.admin_alert_threshold,
                config=config,
            )

    @staticmethod
    def suggest_action(config, count: int) -> str:
        """
        Suggest the next disciplinary action based on thresholds.

        Args:
            config: Escalation config instance.
            count: Current active warning count.

        Returns:
            Suggested action label.
        """
        if (
            config.auto_suspension_threshold
            and count >= config.auto_suspension_threshold
        ):
            return "Suspension Recommended"

        if (
            config.auto_probation_threshold
            and count >= config.auto_probation_threshold
        ):
            return "Probation Recommended"

        return "No Action"

    @staticmethod
    def _notify_warning_issued(
        *,
        warning: WriterWarning,
        triggered_by=None,
    ) -> None:
        """
        Notify the writer that a warning has been issued.

        Args:
            warning: Created warning instance.
            triggered_by: User who issued it, or None for system.
        """
        writer = warning.writer
        user = getattr(writer, "user", None)
        website = getattr(writer, "website", None)

        if not user or not website:
            return

        NotificationService.notify(
            event_key="writer.discipline.warning_issued",
            recipient=user,
            website=website,
            context={
                "writer_id": writer.id,
                "writer_name": user.get_full_name() or user.username,
                "warning_id": warning.id,
                "warning_reason": warning.reason,
                "issued_at": warning.created_at.isoformat(),
                "expires_at": (
                    warning.expires_at.isoformat()
                    if warning.expires_at
                    else None
                ),
                "active_warning_count": (
                    WriterWarningService.get_active_warning_count(writer)
                ),
            },
            triggered_by=triggered_by,
        )

    @staticmethod
    def _notify_warning_threshold(
        *,
        writer: WriterProfile,
        warnings: int,
        threshold: int,
        config,
    ) -> None:
        """
        Notify admins when a writer crosses the warning threshold.

        Args:
            writer: Writer profile that crossed the threshold.
            warnings: Current active warning count.
            threshold: Admin alert threshold.
            config: Escalation config instance.
        """
        website = getattr(writer, "website", None)
        user = getattr(writer, "user", None)

        if not website or not user:
            return

        admin_users = WriterWarningService._get_admin_recipients(website)
        suggested_action = WriterWarningService.suggest_action(
            config,
            warnings,
        )

        for admin in admin_users:
            NotificationService.notify(
                event_key=(
                    "writer.discipline.warning_threshold_reached"
                ),
                recipient=admin,
                website=website,
                context={
                    "writer_id": writer.id,
                    "writer_name": (
                        user.get_full_name() or user.username
                    ),
                    "warning_count": warnings,
                    "threshold": threshold,
                    "suggested_action": suggested_action,
                },
                triggered_by=None,
                is_critical=True,
            )

    @staticmethod
    def _get_admin_recipients(website):
        """
        Resolve admin recipients for a website.

        Args:
            website: Website instance.

        Returns:
            QuerySet of active admin users.
        """
        return User.objects.filter(
            website=website,
            role__in=["admin", "superadmin"],
            is_active=True,
        )