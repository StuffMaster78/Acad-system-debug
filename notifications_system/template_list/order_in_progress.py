from notifications_system.registry.template_registry import (
    register_template_class, BaseNotificationTemplate
)

class OrderInProgressTemplate(BaseNotificationTemplate):
    event_name = "order.in_progress"

    def render(self, ctx):
        order_id = ctx.get("order_id")
        title = f"Order #{order_id} is now in progress"
        text = f"Your order #{order_id} is being processed."
        html = f"<h3>{title}</h3><p>{text}</p>"
        return title, text, html

register_template_class(OrderInProgressTemplate)