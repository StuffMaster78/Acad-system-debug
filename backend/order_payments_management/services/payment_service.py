"""
Compatibility payment service for legacy order payment callers.
"""


class OrderPaymentService:
    @staticmethod
    def process_wallet_payment(payment):
        payment.status = "completed"
        payment.save(update_fields=["status"])
        return payment

    @staticmethod
    def mark_as_external_pending(payment):
        payment.status = "pending"
        payment.save(update_fields=["status"])
        return payment
