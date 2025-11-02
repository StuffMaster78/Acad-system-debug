"""
Payment notification templates.
"""
from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import register_template


@register_template("payment.completed")
class PaymentCompletedTemplate(BaseNotificationTemplate):
    """Notification when payment is completed."""
    
    def get_title(self, payload: dict) -> str:
        order_id = payload.get("order_id", "N/A")
        amount = payload.get("amount", "0.00")
        return f"Payment Completed - ${amount}"
    
    def get_message(self, payload: dict) -> str:
        order_id = payload.get("order_id", "N/A")
        amount = payload.get("amount", "0.00")
        payment_method = payload.get("payment_method", "payment method")
        return (
            f"Your payment of ${amount} for order #{order_id} has been "
            f"successfully processed via {payment_method}. Your order is now "
            f"being processed."
        )
    
    def get_link(self, payload: dict) -> str:
        order_id = payload.get("order_id")
        return f"/orders/{order_id}" if order_id else None


@register_template("payment.failed")
class PaymentFailedTemplate(BaseNotificationTemplate):
    """Notification when payment fails."""
    
    def get_title(self, payload: dict) -> str:
        order_id = payload.get("order_id", "N/A")
        return f"Payment Failed - Order #{order_id}"
    
    def get_message(self, payload: dict) -> str:
        order_id = payload.get("order_id", "N/A")
        reason = payload.get("reason", "Unknown reason")
        amount = payload.get("amount", "0.00")
        return (
            f"Your payment of ${amount} for order #{order_id} could not be "
            f"processed. Reason: {reason}. Please try again or contact support."
        )
    
    def get_link(self, payload: dict) -> str:
        order_id = payload.get("order_id")
        return f"/orders/{order_id}/pay" if order_id else "/support"


@register_template("payment.refunded")
class PaymentRefundedTemplate(BaseNotificationTemplate):
    """Notification when payment is refunded."""
    
    def get_title(self, payload: dict) -> str:
        amount = payload.get("amount", "0.00")
        return f"Refund Processed - ${amount}"
    
    def get_message(self, payload: dict) -> str:
        order_id = payload.get("order_id", "N/A")
        amount = payload.get("amount", "0.00")
        reason = payload.get("reason", "")
        message = (
            f"A refund of ${amount} for order #{order_id} has been processed. "
        )
        if reason:
            message += f"Reason: {reason}. "
        message += "The refund should appear in your account within 5-10 business days."
        return message
    
    def get_link(self, payload: dict) -> str:
        order_id = payload.get("order_id")
        return f"/orders/{order_id}" if order_id else "/account/payments"


@register_template("payment.installment_due")
class InstallmentDueTemplate(BaseNotificationTemplate):
    """Notification when installment payment is due."""
    
    def get_title(self, payload: dict) -> str:
        amount = payload.get("amount", "0.00")
        return f"Installment Payment Due - ${amount}"
    
    def get_message(self, payload: dict) -> str:
        order_id = payload.get("order_id") or payload.get("special_order_id") or "N/A"
        amount = payload.get("amount", "0.00")
        due_date = payload.get("due_date", "")
        installment_number = payload.get("installment_number", 1)
        total_installments = payload.get("total_installments", 1)
        
        message = (
            f"Your installment payment #{installment_number} of {total_installments} "
            f"for ${amount} is due"
        )
        if due_date:
            message += f" by {due_date}"
        message += f" for order #{order_id}. Please make your payment to continue."
        return message
    
    def get_link(self, payload: dict) -> str:
        order_id = payload.get("order_id")
        special_order_id = payload.get("special_order_id")
        if special_order_id:
            return f"/special-orders/{special_order_id}/pay"
        return f"/orders/{order_id}/pay" if order_id else "/payments"


@register_template("payment.wallet_loaded")
class WalletLoadedTemplate(BaseNotificationTemplate):
    """Notification when wallet is loaded."""
    
    def get_title(self, payload: dict) -> str:
        amount = payload.get("amount", "0.00")
        return f"Wallet Loaded - ${amount}"
    
    def get_message(self, payload: dict) -> str:
        amount = payload.get("amount", "0.00")
        balance = payload.get("balance", "0.00")
        return (
            f"Your wallet has been loaded with ${amount}. "
            f"Your current balance is ${balance}. "
            f"You can now use your wallet balance for future orders."
        )
    
    def get_link(self, payload: dict) -> str:
        return "/account/wallet"


@register_template("payment.invoice_generated")
class InvoiceGeneratedTemplate(BaseNotificationTemplate):
    """Notification when invoice is generated."""
    
    def get_title(self, payload: dict) -> str:
        invoice_number = payload.get("invoice_number", "N/A")
        return f"Invoice #{invoice_number} Generated"
    
    def get_message(self, payload: dict) -> str:
        invoice_number = payload.get("invoice_number", "N/A")
        amount = payload.get("amount", "0.00")
        due_date = payload.get("due_date", "")
        message = (
            f"Your invoice #{invoice_number} for ${amount} has been generated. "
        )
        if due_date:
            message += f"Payment is due by {due_date}. "
        message += "Please make your payment to continue with your order."
        return message
    
    def get_link(self, payload: dict) -> str:
        invoice_id = payload.get("invoice_id")
        return f"/invoices/{invoice_id}" if invoice_id else "/invoices"

