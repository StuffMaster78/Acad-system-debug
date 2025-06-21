
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





import importlib
import pkgutil
import sys

def autodiscover_actions():
    """
    Imports all modules in this package to trigger decorators.
    """
    package = sys.modules[__name__]
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{__name__}.{module_name}"
        importlib.import_module(full_module_name)

# Auto-trigger when imported
autodiscover_actions()