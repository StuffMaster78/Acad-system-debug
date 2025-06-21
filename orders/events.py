from writer_management.services.webhook_settings_service import WebhookSettingService
from orders.order_enums import WebhookEvent

def emit_order_event(event_type, order, actor=None):
    """
    Emit an order-related event to all subscribed webhooks.

    Args:
        event_type (str): One of WebhookEvent values.
        order (Order): The Order instance.
        actor (User): Optional user who triggered the event.
    """
    WebhookSettingService.send_event_to_subscribers(
        event_type=event_type,
        order=order,
        actor=actor
    )