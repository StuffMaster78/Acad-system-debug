from __future__ import annotations

from rest_framework.exceptions import APIException, PermissionDenied


class TicketAPIException(APIException):
    status_code = 400
    default_detail = "Ticket request could not be completed."
    default_code = "ticket_error"


class TicketTransitionError(TicketAPIException):
    default_detail = "Ticket status transition is not allowed."
    default_code = "ticket_transition_error"


class TicketPermissionDenied(PermissionDenied):
    default_detail = "You do not have access to this ticket."
    default_code = "ticket_permission_denied"
