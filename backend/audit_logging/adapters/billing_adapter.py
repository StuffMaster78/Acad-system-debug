from audit_logging.adapters.base import BaseAuditAdapter


class BillingAuditAdapter(BaseAuditAdapter):

    def get_domain(self) -> str:
        return "billing"

    def payment_failed(self, invoice_id: str, error: str):
        return self.emit(
            action="billing.payment_failed",
            object_type="invoice",
            object_id=invoice_id,
            metadata={"error": error},
            is_sensitive=True,
        )

    def payment_succeeded(self, invoice_id: str, amount: float):
        return self.emit(
            action="billing.payment_succeeded",
            object_type="invoice",
            object_id=invoice_id,
            metadata={"amount": amount},
        )