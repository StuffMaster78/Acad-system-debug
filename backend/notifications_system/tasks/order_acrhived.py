from notifications_system.registry.template_registry import (
    register_template_class, BaseNotificationTemplate
)
class OrderArchivedTemplate(BaseNotificationTemplate):
    event_name = "order.archived"

    def render(self, ctx):
        order_id = ctx.get("order_id")
        title = f"Order #{order_id} has been archived"
        text = f"Your order #{order_id} has been archived."
        html = f"<h3>{title}</h3><p>{text}</p>"
        return title, text, html
    
register_template_class(OrderArchivedTemplate)