from notifications_system.registry.template_registry import (
    register_template_class, BaseNotificationTemplate
)

class OrderCancellationRequestedTemplate(BaseNotificationTemplate):
    event_name = "order.cancellation_requested"

    def render(self, ctx):
        order_id = ctx.get("order_id")
        title = f"Order #{order_id} Cancellation Requested"
        text = f"Your request to cancel Order #{order_id} has been received."
        html = f"<h3>{title}</h3><p>{text}</p>"
        return title, text, html

register_template_class(OrderCancellationRequestedTemplate)