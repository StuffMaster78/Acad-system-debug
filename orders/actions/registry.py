from .base import OrderActionRegistry
from actions.order_actions import (TransitionToPending,
                      PutOnHold, ResumeOrder, AssignWriter,
                      CompleteOrder, DisputeOrder, ApproveOrder,
                      CancelOrder, ArchiveOrder, LateOrder,
                      RevisionOrder, RequestRevisionAction,
                      ProcessRevisionAction, DenyRevisionAction
)


# Registering all actions in the registry
OrderActionRegistry.register("transition_to_pending", TransitionToPending)
OrderActionRegistry.register("put_on_hold", PutOnHold)
OrderActionRegistry.register("resume_order", ResumeOrder)
OrderActionRegistry.register("assign_writer", AssignWriter)
OrderActionRegistry.register("complete_order", CompleteOrder)
OrderActionRegistry.register("dispute_order", DisputeOrder)
OrderActionRegistry.register("approve_order", ApproveOrder)
OrderActionRegistry.register("cancel_order", CancelOrder)
OrderActionRegistry.register("archive_order", ArchiveOrder)
OrderActionRegistry.register("late_order", LateOrder)
OrderActionRegistry.register("revision_order", RevisionOrder)
OrderActionRegistry.register("request_revision", RequestRevisionAction)
OrderActionRegistry.register("process_revision", ProcessRevisionAction)
OrderActionRegistry.register("deny_revision", DenyRevisionAction)
# Optionally, you could also expose a function to list all available actions
def get_all_actions():
    """
    Retrieve all registered actions in the order action registry.
    :return: A dictionary of action names and their corresponding handler classes.
    """
    return OrderActionRegistry._registry