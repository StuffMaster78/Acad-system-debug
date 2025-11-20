from writer_management.models.configs import (
    WriterWarningEscalationConfig
)

class EscalationConfigService:
    @staticmethod
    def get_config(website) -> WriterWarningEscalationConfig:
        config, _ = WriterWarningEscalationConfig.objects.get_or_create(
            website=website,
            defaults={
                "probation_threshold": 3,
                "suspension_threshold": 5,
                "admin_alert_threshold": 7,
                "default_warning_duration_days": 30,
            }
        )
        return config