from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        import orders.signals  # Ensures signals are registered only when apps are ready
        from orders.registry.discover import auto_discover_order_actions
        auto_discover_order_actions()