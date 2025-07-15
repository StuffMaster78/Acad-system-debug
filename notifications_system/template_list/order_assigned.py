from notifications_system.services.templates_registry import (
    register_template, BaseNotificationTemplate
)

@register_template
class OrderAssignedTemplate(BaseNotificationTemplate):
    event_name = "order_assigned"

    def render(self):
        order_id = self.context.get("order_id", "???")
        title = f"New Order #{order_id} Assigned"
        msg = f"You've been assigned Order #{order_id}. Check your account and get started now."
        html = f"<h2>{title}</h2><p>{msg}</p>"
        return title, msg, html
