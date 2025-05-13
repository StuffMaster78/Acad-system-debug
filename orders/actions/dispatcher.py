import logging
import importlib
from django.core.exceptions import ValidationError
from orders.actions.base import OrderActionHandler

logger = logging.getLogger(__name__)

ORDER_ACTION_REGISTRY = {
    "put_on_hold": "orders.actions.PutOnHold",
    "resume_order": "orders.actions.ResumeOrder",
    "assign_writer": "orders.actions.AssignWriter",
    "complete_order": "orders.actions.CompleteOrder",
    "dispute_order": "orders.actions.DisputeOrder",
    "approve_order": "orders.actions.ApproveOrder",
    "cancel_order": "orders.actions.CancelOrder",
    "archive_order": "orders.actions.ArchiveOrder",
    "late_order": "orders.actions.LateOrder",
    "revision_order": "orders.actions.RevisionOrder",
    "transition_to_pending": "orders.actions.TransitionToPending",
}


def import_handler_class(path: str) -> type[OrderActionHandler]:
    """
    Dynamically import a handler class from a string path.
    """
    try:
        module_path, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        handler_class = getattr(module, class_name)

        if not issubclass(handler_class, OrderActionHandler):
            raise TypeError(f"{class_name} is not a subclass of OrderActionHandler")

        return handler_class

    except (ImportError, AttributeError, TypeError) as e:
        logger.exception(f"Failed to import action handler: {path}")
        raise ValidationError(f"Invalid action handler: {str(e)}")


def dispatch_order_action(action_name: str, order, *args, **kwargs):
    """
    Dispatch the given action name to the appropriate OrderActionHandler subclass.
    """
    handler_path = ORDER_ACTION_REGISTRY.get(action_name)
    if not handler_path:
        logger.warning(f"Attempted to dispatch unknown action: {action_name}")
        raise ValidationError(f"Invalid action: '{action_name}'")

    handler_class = import_handler_class(handler_path)

    try:
        handler = handler_class()
        return handler.execute(order, *args, **kwargs)

    except Exception as e:
        logger.exception(f"Error executing '{action_name}' on order {getattr(order, 'id', None)}")
        raise ValidationError(f"Action '{action_name}' failed: {str(e)}")