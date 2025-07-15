from django.apps import AppConfig


class NotificationsSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications_system'


    def ready(self):
        from .services import templates_registry
        import notifications_system.checks  # Ensures checks are registered only when apps are ready
        templates_registry.auto_discover_templates()    # Automatically discover and register notification templates    
        from notifications_system.services.dispatcher import auto_register_notification_handlers
        auto_register_notification_handlers()  # Automatically register notification handlers for events
        from notifications_system.services import dispatcher
        dispatcher.auto_register_notification_dispatchers()  # Automatically register notification dispatchers for events