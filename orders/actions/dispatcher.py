# orders/actions/dispatcher.py

from orders.actions.base import OrderActionHandler
from django_fsm import TransitionNotAllowed  # type: ignore
from django.core.exceptions import ValidationError

ORDER_ACTION_REGISTRY = {
    'put_on_hold': 'orders.actions.PutOnHold',
    'resume_order': 'orders.actions.ResumeOrder',
    'assign_writer': 'orders.actions.AssignWriter',
    'complete_order': 'orders.actions.CompleteOrder',
    'dispute_order': 'orders.actions.DisputeOrder',
    'approve_order': 'orders.actions.ApproveOrder',
    'cancel_order': 'orders.actions.CancelOrder',
    'archive_order': 'orders.actions.ArchiveOrder',
    'late_order': 'orders.actions.LateOrder',
    'revision_order': 'orders.actions.RevisionOrder',
    'transition_to_pending': 'orders.actions.TransitionToPending',
}

def dispatch_order_action(action_name: str, order, *args, **kwargs):
    """
    Dispatches the action to the correct handler.

    :param action_name: The action to perform (e.g., 'assign_writer').
    :param order: The order object to perform the action on.
    :param args: Arguments to pass to the handler's `execute` method.
    :param kwargs: Keyword arguments to pass to the handler's `execute` method.
    :return: The updated order after performing the action.
    :raises: TransitionNotAllowed if the action is not allowed.
    """
    try:
        # Fetch the action handler dynamically from the registry
        handler_class = ORDER_ACTION_REGISTRY.get(action_name)
        if not handler_class:
            raise ValidationError(f"Invalid action name: {action_name}")

        # Dynamically instantiate the handler and call the `execute` method
        handler = globals()[handler_class]()
        return handler.execute(order, *args, **kwargs)
        
    except TransitionNotAllowed as e:
        raise e  # Re-raise the TransitionNotAllowed exception
    except Exception as e:
        raise ValidationError(f"Error performing action: {str(e)}")
