
# from .registry import OrderActionRegistry
# from .order_actions import (TransitionToPending,
#                       PutOnHold, ResumeOrder, AssignWriter,
#                       CompleteOrder, DisputeOrder, ApproveOrder,
#                       CancelOrder, ArchiveOrder, LateOrder,
#                       RevisionOrder)

# __all__ = [
#     "OrderActionRegistry",  # To allow importing of the registry
#     "TransitionToPending", 
#     "PutOnHold", 
#     "ResumeOrder", 
#     "AssignWriter",
#     "CompleteOrder", 
#     "DisputeOrder", 
#     "ApproveOrder", 
#     "CancelOrder", 
#     "ArchiveOrder", 
#     "LateOrder", 
#     "RevisionOrder"
# ]


from .creation import CreateOrderAction
from .hold import HoldOrderAction
from .cancel import CancelOrderAction
from .approve import ApproveOrderAction
from .review import ReviewOrderAction
from .rate import RateOrderAction
from .archive_action import ArchiveAction
from .archive_order import ArchiveOrderAction
from .reopen_order import ReopenOrderAction
from .apply_discount import ApplyDirectDiscountAction
from .apply_discount_code import ApplyDiscountCodeAction
from .assignment import OrderAssignmentAction
from .status_transition import StatusTransitionAction
from .unpaid import UnpaidOrderAction
from .complete import CompleteOrderAction
from .complete_to_approved import CompleteToApprovedAction
from .order_revision import (
    SubmitRevisionAction, DenyRevisionAction,
    ProcessRevisionAction, OrderRevisionAction
)
from .urgency import OrderUrgencyAction
from .pricing_calculator import PricingCalculatorAction
from .mark_critical import MarkCriticalAction
from .mark_late import MarkLateOrderAction
from .preferred_writer import (
    PreferredWriterAction,
    PreferredWriterResponseAction
)
from .order_transition import OrderTransitionAction
from .reassignment import ReassignmentRequestAction
from .move_to_editing import MoveOrderToEditingAction
from .submit import SubmitOrderAction
from .order_revision import DenyRevisionAction
from .order_revision import ProcessRevisionAction
from .mark_paid import MarkOrderPaidAction
from .writer_requests_actions import (
    CreateWriterRequestAction,
    ClientRespondToWriterRequestAction,
    AdminOverrideWriterRequestAction,
)




from .registry import register_action
register_action('create_order', CreateOrderAction)
register_action('hold_order', HoldOrderAction)
register_action('cancel_order', CancelOrderAction)
register_action('complete_order', CompleteOrderAction)
register_action('approve_order', ApproveOrderAction)
register_action('review_order', ReviewOrderAction)
register_action('rate_order', RateOrderAction)
register_action('archive_order', ArchiveOrderAction)
register_action('archive', ArchiveAction)
register_action('reopen_order', ReopenOrderAction)
register_action('apply_direct_discount', ApplyDirectDiscountAction)
register_action('apply_discount_code', ApplyDiscountCodeAction)
register_action('mark_critical', MarkCriticalAction)
register_action('assign_order', OrderAssignmentAction)
register_action('mark_late', MarkLateOrderAction)
register_action('mark_paid', MarkOrderPaidAction)
register_action('order_transition', OrderTransitionAction)
register_action('order_urgency', OrderUrgencyAction)
register_action('preferred_writer', PreferredWriterAction)
register_action('preferred_writer_response', PreferredWriterResponseAction)
register_action('order_revision', OrderRevisionAction)
register_action('status_transition', StatusTransitionAction)
register_action('unpaid_order', UnpaidOrderAction)
register_action('pricing_calculator', PricingCalculatorAction)
register_action('complete_to_approved', CompleteToApprovedAction)
register_action('reassignment_request', ReassignmentRequestAction)
register_action('move_to_editing', MoveOrderToEditingAction)
register_action('submit_order', SubmitOrderAction)
register_action('submit_revision', SubmitRevisionAction)
register_action('deny_revision', DenyRevisionAction)
register_action('process_revision', ProcessRevisionAction)
register_action('create_writer_request', CreateWriterRequestAction)
register_action('client_respond_to_writer_request', ClientRespondToWriterRequestAction)
register_action('admin_override_writer_request', AdminOverrideWriterRequestAction)