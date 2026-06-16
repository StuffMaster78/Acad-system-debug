# Compat shim — PriceService moved to orders.services.old_services.price_service
# Tests referencing PriceService need to be updated to use the new pricing system.
from orders.services.old_services.price_service import PriceService

__all__ = ["PriceService"]
