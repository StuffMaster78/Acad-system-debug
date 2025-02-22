from django.apps import AppConfig


class SpecialOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'special_orders'

    def ready(self):
        import special_orders.signals