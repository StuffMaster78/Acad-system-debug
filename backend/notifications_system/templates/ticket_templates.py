"""
Support ticket notification templates.
"""
from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import register_template


@register_template("ticket.created")
class TicketCreatedTemplate(BaseNotificationTemplate):
    """Notification when ticket is created."""
    
    def get_title(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        return f"Support Ticket #{ticket_number} Created"
    
    def get_message(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        subject = payload.get("subject", "")
        message = f"Your support ticket #{ticket_number} has been created. "
        if subject:
            message += f"Subject: {subject}. "
        message += "Our support team will respond as soon as possible."
        return message
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"


@register_template("ticket.assigned")
class TicketAssignedTemplate(BaseNotificationTemplate):
    """Notification when ticket is assigned to support staff."""
    
    def get_title(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        return f"Ticket #{ticket_number} Assigned"
    
    def get_message(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        assignee_name = payload.get("assignee_name", "a support agent")
        message = (
            f"Support ticket #{ticket_number} has been assigned to {assignee_name}. "
            f"They will review and respond to your request shortly."
        )
        return message
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"


@register_template("ticket.replied")
class TicketRepliedTemplate(BaseNotificationTemplate):
    """Notification when ticket receives a reply."""
    
    def get_title(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        replier_name = payload.get("replier_name", "Support")
        return f"New Reply on Ticket #{ticket_number} from {replier_name}"
    
    def get_message(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        replier_name = payload.get("replier_name", "Support")
        preview = payload.get("message_preview", "")
        if preview and len(preview) > 150:
            preview = preview[:150] + "..."
        message = (
            f"You received a new reply from {replier_name} on ticket #{ticket_number}. "
        )
        if preview:
            message += f'"{preview}"'
        return message
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        message_id = payload.get("message_id")
        if message_id:
            return f"/tickets/{ticket_id}#message-{message_id}"
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"


@register_template("ticket.resolved")
class TicketResolvedTemplate(BaseNotificationTemplate):
    """Notification when ticket is resolved."""
    
    def get_title(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        return f"Ticket #{ticket_number} Resolved"
    
    def get_message(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        resolver_name = payload.get("resolver_name", "Support")
        resolution = payload.get("resolution", "")
        message = (
            f"Your support ticket #{ticket_number} has been marked as resolved by {resolver_name}. "
        )
        if resolution:
            message += f"Resolution: {resolution} "
        message += "If you need further assistance, please reopen the ticket."
        return message
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"


@register_template("ticket.reopened")
class TicketReopenedTemplate(BaseNotificationTemplate):
    """Notification when ticket is reopened."""
    
    def get_title(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        return f"Ticket #{ticket_number} Reopened"
    
    def get_message(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        return (
            f"Your support ticket #{ticket_number} has been reopened. "
            f"Our team will review your request and respond shortly."
        )
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"


@register_template("ticket.escalated")
class TicketEscalatedTemplate(BaseNotificationTemplate):
    """Notification when ticket is escalated."""
    
    def get_title(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        return f"Ticket #{ticket_number} Escalated"
    
    def get_message(self, payload: dict) -> str:
        ticket_number = payload.get("ticket_number", "N/A")
        escalated_to = payload.get("escalated_to", "senior support")
        reason = payload.get("reason", "")
        message = (
            f"Your support ticket #{ticket_number} has been escalated to {escalated_to}. "
        )
        if reason:
            message += f"Reason: {reason}. "
        message += "They will prioritize your request."
        return message
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"

