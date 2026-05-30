"""
Support Management Services
"""
from .analytics_service import SupportAnalyticsService
from .dispute_resolution_service import DisputeResolutionService
from .escalation_service import EscalationService
from .performance_service import SupportPerformanceService
from .reassignment_service import SmartReassignmentService
from .sla_service import SLAService
from .ticket_assignment_service import TicketAssignmentService

__all__ = [
    "DisputeResolutionService",
    "EscalationService",
    "SLAService",
    "SmartReassignmentService",
    "SupportAnalyticsService",
    "SupportPerformanceService",
    "TicketAssignmentService",
]

