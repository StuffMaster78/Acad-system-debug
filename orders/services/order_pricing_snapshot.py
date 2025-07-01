from orders.models import Order, OrderPricingSnapshot
from orders.services.pricing_calculator import PricingCalculatorService # assuming you have this
from django.utils.timezone import now

class OrderPricingSnapshotService:
    """Service to manage order pricing snapshots."""
    @staticmethod
    def save_snapshot(order, pricing_data):
        OrderPricingSnapshot.objects.update_or_create(
            order=order,
            defaults={
                "pricing_data": pricing_data,
                "calculated_at": now()
            }
        )[0]

    @staticmethod
    def create_snapshot(order: Order):
        calculator = PricingCalculatorService(order)
        pricing_data = calculator.calculate(full=True)

        required_keys = ["base_price", "final_total"]
        if not pricing_data or not all(k in pricing_data for k in required_keys):
            raise ValueError("Incomplete pricing breakdown.")
        
        return OrderPricingSnapshotService.save_snapshot(order, pricing_data)