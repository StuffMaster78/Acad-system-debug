from django.apps import AppConfig


class SpecialOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'special_orders'

    def ready(self):
        try:
            import special_orders.signals  # noqa: F401
        except Exception:
            pass
