from django.apps import AppConfig


class ClassManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'class_management'

    def ready(self):
        import class_management.signals
