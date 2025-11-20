from __future__ import annotations

from django.template.loader import render_to_string
from notifications_system.registry.template_registry import (
    register_template_class,
    BaseNotificationTemplate,
)


class OrderPaidTemplate(BaseNotificationTemplate):
    event_name = "order.paid"

    def render(self, ctx):
        title = ctx.get("title", "Payment received")
        text = ctx.get("message", "")
        html = render_to_string("notifications/order_paid.html", ctx)
        return title, text, html


register_template_class("order.paid")(OrderPaidTemplate)



