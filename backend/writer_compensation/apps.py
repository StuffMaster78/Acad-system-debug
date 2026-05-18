from django.apps import AppConfig


class WriterCompensationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'writer_compensation'
    # label = 'writer_compensation'
    # verbose_name = 'Writer Compensation'


    def ready(self):
        import writer_compensation.handlers.compensation_handlers  # noqa: F401
        import writer_compensation.signals.reward_signals # noqa: F401 