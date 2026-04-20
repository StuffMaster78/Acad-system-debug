"""
App configuration for the orders_pricing_core app.
"""

from __future__ import annotations

from django.apps import AppConfig


class OrdersPricingCoreConfig(AppConfig):
    """
    Django app configuration for orders_pricing_core.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "order_pricing_core"
    verbose_name = "Order Pricing Core"

    def ready(self) -> None:
        """
        Import signal handlers when the app is ready.

        Importing inside ready avoids circular import issues during
        app loading.
        """
        try:
            import order_pricing_core.signals  # noqa: F401
        except ImportError:
            pass