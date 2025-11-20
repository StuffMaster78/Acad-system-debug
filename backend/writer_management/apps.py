from django.apps import AppConfig

class WriterManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'writer_management'

    def ready(self):
        import writer_management.signals
        import writer_management.writer_status_signals
        from .notification_handlers import writer_role_resolver
        from notifications_system.registry.role_registry import register_role

        register_role(
            "writer",
            writer_role_resolver,
            channels={
                "badge.awarded": {"in_app", "email"},
                "badge.revoked": {"in_app", "email"},
                "badge.milestone": {"in_app", "email"},
            },
        )