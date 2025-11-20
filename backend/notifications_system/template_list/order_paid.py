# notifications_system/templates/order_paid.py
from notifications_system.registry.template_registry import (
    register_template_class, BaseNotificationTemplate
)

class OrderPaidTemplate(BaseNotificationTemplate):
    event_name = "order.paid"

    def render(self, ctx):
        order_id = ctx.get("order_id")
        amount   = ctx.get("amount")
        currency = ctx.get("currency", "USD")
        title = f"Payment received for Order #{order_id}"
        text  = f"We've received your payment of {amount} {currency}."
        html  = (
            f"<h3>{title}</h3>"
            f"<p>Amount: <strong>{amount} {currency}</strong></p>"
        )
        return title, text, html
    
register_template_class(OrderPaidTemplate)