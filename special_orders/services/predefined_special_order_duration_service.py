"""
Service class to manage PredefinedSpecialOrderDuration operations.
"""

from special_orders.models import PredefinedSpecialOrderDuration, PredefinedSpecialOrderConfig


class PredefinedSpecialOrderDurationService:
    """
    Handles creation and retrieval of durations for predefined special orders.
    """

    @staticmethod
    def create_order_duration(predefined_order: PredefinedSpecialOrderConfig,
                              duration_days: int, price: float):
        """
        Creates a new duration entry for a predefined special order.

        Args:
            predefined_order (PredefinedSpecialOrderConfig): The predefined
                special order configuration.
            duration_days (int): Duration of the order in days.
            price (float): Price for the order duration.

        Returns:
            PredefinedSpecialOrderDuration: The created duration object.
        """
        return PredefinedSpecialOrderDuration.objects.create(
            predefined_order=predefined_order,
            duration_days=duration_days,
            price=price
        )

    @staticmethod
    def get_duration_for_order(predefined_order: PredefinedSpecialOrderConfig,
                               duration_days: int):
        """
        Retrieves the duration and price for a specific predefined special
        order and duration.

        Args:
            predefined_order (PredefinedSpecialOrderConfig): The predefined
                special order configuration.
            duration_days (int): Duration of the special order in days.

        Returns:
            PredefinedSpecialOrderDuration: Duration object, or None if
            not found.
        """
        return PredefinedSpecialOrderDuration.objects.filter(
            predefined_order=predefined_order,
            duration_days=duration_days
        ).first()

    def get_all_durations():
        """Return all predefined special order durations."""
        return PredefinedSpecialOrderDuration.objects.all()