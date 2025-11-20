from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core.cache import cache
from orders.models import Order, PreferredWriterResponse
from django.contrib.auth import get_user_model
from pricing_configs.models import PreferredWriterConfig

User = get_user_model()


CACHE_KEY_PREFERRED_WRITER_COST = "preferred_writer_cost"
CACHE_TIMEOUT = 60 * 60  # 1 hour

class PreferredWriterService:
    """
    Service to handle preferred writer related operations, including
    responding to preferred orders and retrieving recent writers for a client.
    """
    def get_preferred_writer_cost() -> Decimal:
        """
        Return cached preferred writer cost or fetch from DB and cache it.
        """
        cost = cache.get(CACHE_KEY_PREFERRED_WRITER_COST)
        if cost is not None:
            return cost

        try:
            pricing_config = PreferredWriterConfig.objects.first()
            cost = pricing_config.preferred_writer_cost if pricing_config else Decimal(0)
        except PreferredWriterConfig.DoesNotExist:
            cost = Decimal(0)

        cache.set(CACHE_KEY_PREFERRED_WRITER_COST, cost, CACHE_TIMEOUT)
        return cost
    @staticmethod
    def calculate_preferred_writer_fee(order) -> Decimal:
        """
        Calculates the additional fee for selecting a preferred writer.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The additional fee for the preferred writer, or 0 if none.
        """
        if not order.preferred_writer:
            return Decimal(0)
        return PreferredWriterService.get_preferred_writer_cost()

    @staticmethod
    def get_last_five_writers_for_client(client):
        """
        Retrieves the last 5 writers a client has worked with, ordered by most
        recent order deadline.

        Args:
            client (User): The client user instance.

        Returns:
            QuerySet[User]: Queryset of up to 5 writer User instances.
        """
        return (
            Order.objects.filter(client=client, preferred_writer__isnull=False)
            .order_by('-deadline')
            .values_list('preferred_writer', flat=True)
            .distinct()[:5]
        )