# writer_management/services/writer_warning_service.py

from django.utils.timezone import now
from datetime import timedelta

from writer_management.models.writer_warnings import WriterWarning
from writer_management.models.profile import WriterProfile
from writer_management.services.escalation_config_service import (
    EscalationConfigService,
)
from writer_management.services.discipline_notification_service import (
    DisciplineNotificationService,
)


class WriterWarningService:
    @staticmethod
    def issue_warning(
        writer: WriterProfile,
        reason: str,
        issued_by=None,
        expires_days: int = None
    ) -> WriterWarning:
        config = EscalationConfigService.get_config(writer.website)
        expires_days = expires_days or config.default_warning_duration_days
        expires_at = now() + timedelta(days=expires_days)

        warning = WriterWarning.objects.create(
            website=writer.website,
            writer=writer,
            reason=reason,
            issued_by=issued_by,
            expires_at=expires_at,
        )

        WriterWarningService.check_threshold(writer)
        return warning

    @staticmethod
    def get_active_warning_count(writer: WriterProfile) -> int:
        return writer.warnings.filter(
            is_active=True,
            expires_at__gt=now()
        ).count()

    @staticmethod
    def check_threshold(writer: WriterProfile) -> None:
        config = EscalationConfigService.get_config(writer.website)
        count = WriterWarningService.get_active_warning_count(writer)

        if count >= config.admin_alert_threshold:
            DisciplineNotificationService.notify_warning_threshold(
                writer,
                warnings=count,
                threshold=config.admin_alert_threshold,
            )

    @staticmethod
    def suggest_action(config, count) -> str:
        if (
            config.auto_suspension_threshold and
            count >= config.auto_suspension_threshold
        ):
            return "Suspension Recommended"
        elif (
            config.auto_probation_threshold and
            count >= config.auto_probation_threshold
        ):
            return "Probation Recommended"
        return "No Action"

