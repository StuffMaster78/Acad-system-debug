from __future__ import annotations


class TicketRole:
    STAFF_ROLES = {"admin", "superadmin", "support", "editor"}
    USER_ROLES = {"client", "writer"}


class TicketAction:
    CREATED = "ticket.created"
    ASSIGNED = "ticket.assigned"
    ESCALATED = "ticket.escalated"
    CLOSED = "ticket.closed"
    REOPENED = "ticket.reopened"
    MESSAGE_ADDED = "ticket.message_added"
    FILE_ATTACHED = "ticket.file_attached"
