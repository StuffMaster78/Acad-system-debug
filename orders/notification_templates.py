from notifications_system.registry.template_registry import (
    register_template,
    BaseNotificationTemplate,
    register_template_name
)


@register_template("order.assigned")
class OrderAssignedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order Assigned")
        message = self.context.get(
            "message", "You have been assigned to a new order."
        )
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    

@register_template("order.on_hold")
class OrderOnHoldTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order On Hold")
        message = self.context.get("message", "Your order is currently on hold.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    
@register_template("order.on_revision")
class OrderOnRevisionTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order On Revision")
        message = self.context.get("message", "Your order is under revision.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

@register_template("order.completed")
class OrderCompletedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order Completed")
        message = self.context.get("message", "Your order has been completed.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    

@register_template("order.revision_requested")
class OrderRevisionRequestedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Revision Requested")
        message = self.context.get("message", "A revision has been requested for your order.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

@register_template("order.revision_complete")
class OrderRevisionCompleteTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Revision Complete")
        message = self.context.get("message", "The revision for your order is complete.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

    @classmethod
    def from_order(cls, order):
        instance = cls()
        instance.context = {
            "title": f"Revision Complete for Order {order.id}",
            "message": f"The revision for your order {order.id} is complete."
        }
        return instance

@register_template("order.cancelled")
class OrderCancelledTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order Cancelled")
        message = self.context.get("message", "Your order has been cancelled.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    


@register_template("order.refunded")
class OrderRefundedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order Refunded")
        message = self.context.get("message", "Your order has been refunded.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

@register_template("order.preferred_writer")
class OrderPreferredWriterTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Preferred Writer Assigned")
        message = self.context.get("message", "A preferred writer has been assigned to your order.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

@register_template("order.in_progress")
class OrderInProgressTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order In Progress")
        message = self.context.get("message", "Your order is currently in progress.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

@register_template("order.under_editing")
class OrderUnderEditingTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Order Under Editing")
        message = self.context.get("message", "Your order is currently being edited.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    

@register_template("order.writer_assigned")
class OrderWriterAssignedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Writer Assigned")
        message = self.context.get("message", "A writer has been assigned to your order.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    
@register_template("order.writer_reassigned")
class OrderWriterReassignedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Writer Reassigned")
        message = self.context.get("message", "A writer has been reassigned to your order.")
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    

@register_template("order.writer_unassigned")
class OrderWriterUnassignedTemplate(BaseNotificationTemplate):
    def render(self):
        title = self.context.get("title", "Writer Unassigned")
        message = self.context.get(
            "message",
            "We have reassigned the current writer has been unassigned from your order. Another writer will be assigned to it shortly."
        )
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html
    

@register_template("order.available")
class OrderAvailableTemplate(BaseNotificationTemplate):
    def render(self, order):
        title = self.context.get("title", "Order Available")
        message = self.context.get(
            "message",
            f"Your order - {order.id} is now available. Writers will show interest and be assigned shortly."
        )
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

@register_template("order.payment_received")
class OrderPaymentReceivedTemplate(BaseNotificationTemplate):
    """
    context will contain whatever the caller passed to 
    NotificationService.send_notification(...)
    e.g. {"order_id": 123, "title": "...", "message": "...", ...}
    """
    def render(self, order):
        title = self.context.get("title", "Payment Received")
        message = self.context.get(
            "message",
            f"We have received the payment for your order {order.id}."
        )
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

    @classmethod
    def from_order(cls, order):
        instance = cls()
        instance.context = {
            "title": f"Payment Received for Order {order.id}",
            "message": f"We have received the payment for your order {order.id}."
        }
        return instance

@register_template("order.paid")
class OrderPaidTemplate(BaseNotificationTemplate):
    """
    context will contain whatever the caller passed to 
    NotificationService.send_notification(...)
    e.g. {"order_id": 123, "title": "...", "message": "...", ...}
    """
    def render(self, order):
        title = self.context.get("title", "Order Paid")
        message = self.context.get(
            "message",
            f"Your order {order.id} has been paid."
        )
        html = f"<strong>{title}</strong><br>{message}"
        return title, message, html

    # Optional helper if you like constructing the context from a model
    @classmethod
    def from_order(cls, order):
        instance = cls()
        instance.context = {
            "title": f"Payment Received for Order {order.id}",
            "message": f"We have received the payment for your order {order.id}."
        }
        return instance 
    


    # (Optional) If you also want a specific email template file for this event:
register_template_name(
    event_key="order.paid",
    channel="email",
    template_name="notifications/emails/order_paid.html"
)


register_template_name(
    event_key="order.restored",
    channel="email",
    template_name="notifications/emails/order_restored.html"
)