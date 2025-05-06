"""
Service class to manage PredefinedSpecialOrderConfig operations.
"""

from websites.models import Website
from special_orders.models import PredefinedSpecialOrderConfig


class PredefinedSpecialOrderConfigService:
    """
    Handles creation, update, and retrieval of predefined
    special order configurations.
    """

    @staticmethod
    def create_order_config(website: Website, name: str, description: str,
                            is_active: bool):
        """
        Creates a predefined special order configuration.

        Args:
            website (Website): The associated website.
            name (str): Name of the order type.
            description (str): Description of the order type.
            is_active (bool): Active status of the configuration.

        Returns:
            PredefinedSpecialOrderConfig: Created config object.
        """
        return PredefinedSpecialOrderConfig.objects.create(
            website=website,
            name=name,
            description=description,
            is_active=is_active
        )

    @staticmethod
    def update_order_config(config: PredefinedSpecialOrderConfig, name: str,
                            description: str, is_active: bool):
        """
        Updates a predefined special order configuration.

        Args:
            config (PredefinedSpecialOrderConfig): Config to update.
            name (str): New name.
            description (str): New description.
            is_active (bool): New active status.

        Returns:
            PredefinedSpecialOrderConfig: Updated config object.
        """
        config.name = name
        config.description = description
        config.is_active = is_active
        config.save()
        return config

    @staticmethod
    def get_active_configs_for_website(website: Website):
        """
        Gets active predefined order configs for a given website.

        Args:
            website (Website): The website.

        Returns:
            QuerySet: Active configuration objects.
        """
        return PredefinedSpecialOrderConfig.objects.filter(
            website=website,
            is_active=True
        )

    def get_all_configs():
        """Return all predefined special order configurations."""
        return PredefinedSpecialOrderConfig.objects.all()