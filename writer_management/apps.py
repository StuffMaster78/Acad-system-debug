from django.apps import AppConfig

class WriterManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'writer_management'

    def ready(self):
        import writer_management.signals