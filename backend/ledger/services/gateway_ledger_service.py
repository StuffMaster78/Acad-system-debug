# Compat shim — GatewayLedgerService renamed to PaymentProcessorLedgerService.
from ledger.services.payment_processor_ledger_service import PaymentProcessorLedgerService as GatewayLedgerService

__all__ = ["GatewayLedgerService"]
