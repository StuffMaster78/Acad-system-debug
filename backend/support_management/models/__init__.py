"""
Support Management Models Package
Main models are in support_management.models (parent file)
This package contains additional models like OrderDispute, DisputeMessage
"""
# Import all from parent models.py using importlib to avoid circular import
import importlib.util
from pathlib import Path

_parent_models = Path(__file__).parent.parent / 'models.py'
if _parent_models.exists():
    spec = importlib.util.spec_from_file_location("support_management.models_main", _parent_models)
    if spec and spec.loader:
        models_main = importlib.util.module_from_spec(spec)
        models_main.__package__ = 'support_management'
        spec.loader.exec_module(models_main)
        # Explicitly export all models from parent
        SupportProfile = models_main.SupportProfile
        SupportMessage = models_main.SupportMessage
        SupportMessageAccess = models_main.SupportMessageAccess
        SupportGlobalAccess = models_main.SupportGlobalAccess
        SupportPermission = models_main.SupportPermission
        SupportNotification = models_main.SupportNotification
        DisputeResolutionLog = models_main.DisputeResolutionLog
        SupportActionLog = models_main.SupportActionLog
        EscalationLog = models_main.EscalationLog
        SupportAvailability = models_main.SupportAvailability
        SupportActivityLog = models_main.SupportActivityLog
        PaymentIssueLog = models_main.PaymentIssueLog
        SupportOrderFileManagement = models_main.SupportOrderFileManagement
        SupportOrderManagement = models_main.SupportOrderManagement
        WriterPerformanceLog = models_main.WriterPerformanceLog
        SupportWorkloadTracker = models_main.SupportWorkloadTracker
        OrderDisputeSLA = models_main.OrderDisputeSLA
        FAQCategory = models_main.FAQCategory
        FAQManagement = models_main.FAQManagement
        SupportDashboard = models_main.SupportDashboard
    else:
        # Fallback - set to None if import fails
        SupportProfile = None
        SupportMessage = None
        SupportMessageAccess = None
        SupportGlobalAccess = None
        SupportPermission = None
        SupportNotification = None
        DisputeResolutionLog = None
        SupportActionLog = None
        EscalationLog = None
        SupportAvailability = None
        SupportActivityLog = None
        PaymentIssueLog = None
        SupportOrderFileManagement = None
        SupportOrderManagement = None
        WriterPerformanceLog = None
        SupportWorkloadTracker = None
        OrderDisputeSLA = None
        FAQCategory = None
        FAQManagement = None
        SupportDashboard = None
else:
    # Fallback - set to None if file doesn't exist
    SupportProfile = None
    SupportMessage = None
    SupportMessageAccess = None
    SupportGlobalAccess = None
    SupportPermission = None
    SupportNotification = None
    DisputeResolutionLog = None
    SupportActionLog = None
    EscalationLog = None
    SupportAvailability = None
    SupportActivityLog = None
    PaymentIssueLog = None
    SupportOrderFileManagement = None
    SupportOrderManagement = None
    WriterPerformanceLog = None
    SupportWorkloadTracker = None
    OrderDisputeSLA = None
    FAQCategory = None
    FAQManagement = None
    SupportDashboard = None

# Import from this package
try:
    from .enhanced_disputes import OrderDispute, DisputeMessage
except ImportError:
    OrderDispute = None
    DisputeMessage = None

__all__ = [
    'SupportProfile', 'SupportNotification', 'SupportOrderManagement',
    'SupportMessage', 'SupportMessageAccess', 'SupportGlobalAccess',
    'SupportPermission', 'DisputeResolutionLog', 'SupportActionLog',
    'EscalationLog', 'SupportAvailability', 'SupportActivityLog',
    'PaymentIssueLog', 'SupportOrderFileManagement', 'WriterPerformanceLog',
    'SupportWorkloadTracker', 'OrderDisputeSLA', 'FAQCategory', 'FAQManagement',
    'SupportDashboard', 'OrderDispute', 'DisputeMessage'
]

