class DeliveryValidator:
    """
    Enforces funding gates before delivery.
    """

    @staticmethod
    def validate_can_deliver(*, funding_plan):
        if funding_plan.status != "funded":
            raise ValueError("Order must be fully funded before delivery.")

    @staticmethod
    def validate_can_start(*, funding_plan):
        if funding_plan.status not in ["partially_funded", "funded"]:
            raise ValueError("Order cannot start without funding.")