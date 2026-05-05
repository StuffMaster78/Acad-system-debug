from __future__ import annotations

from class_management.integration.communication_adapter import (
    ClassCommunicationAdapter,
)
from communications.integrations.registry import (
    CommunicationAdapterRegistry,
)
from orders.integrations.communication_adapter import (
    OrderCommunicationAdapter,
)
from special_orders.integrations.communication_adapter import (
    SpecialOrderCommunicationAdapter,
)

# Import models
from class_management.models import ClassOrder
from orders.models import Order
from special_orders.models import SpecialOrder


def register_communication_adapters() -> None:
    """
    Register all communication adapters.
    """
    CommunicationAdapterRegistry.register(
        model=Order,
        adapter=OrderCommunicationAdapter(),
    )

    CommunicationAdapterRegistry.register(
        model=ClassOrder,
        adapter=ClassCommunicationAdapter(),
    )

    CommunicationAdapterRegistry.register(
        model=SpecialOrder,
        adapter=SpecialOrderCommunicationAdapter(),
    )