from notifications_system.services.templates_registry import (
    register_template, BaseNotificationTemplate
)

@register_template
class OrderCreatedTemplate(BaseNotificationTemplate):
    event_name = "order_created"

    def render(self):
        order_id = self.context.get("order_id", "???")
        title = f"Order #{order_id} Created"
        msg = f"Your order #{order_id} has been successfully created. You can view it in your account."
        html = f"<h2>{title}</h2><p>{msg}</p>"
        return title, msg, html