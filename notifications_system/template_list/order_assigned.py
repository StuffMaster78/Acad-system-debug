from notifications_system.registry.template_registry import (
    register_template_class, BaseNotificationTemplate
)

@register_template_class
class OrderAssignedTemplate(BaseNotificationTemplate):
    event_name = "order_assigned"

    def render(self):
        order_id = self.context.get("order_id", "???")
        title = f"New Order #{order_id} Assigned"
        msg = (
            f"You've been assigned Order #{order_id}. "
            f"Check your account and get started now."
        )
        html = f"<h2>{title}</h2><p>{msg}</p>"
        return title, msg, html
