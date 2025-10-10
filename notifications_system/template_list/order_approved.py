from notifications_system.registry.template_registry import (
    register_template_class, BaseNotificationTemplate
)

class OrderApprovedTemplate(BaseNotificationTemplate):
    event_name = "order.approved"

    def render(self, ctx):
        order_id = ctx.get("order_id")
        title = f"Order #{order_id} has been approved"
        text = f"Your order #{order_id} has been approved."
        html = f"<h3>{title}</h3><p>{text}</p>"
        return title, text, html

register_template_class(OrderApprovedTemplate)
