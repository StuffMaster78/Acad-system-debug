"""
Class management notification templates.
"""
from notifications_system.templates.base import BaseNotificationTemplate
from notifications_system.registry.template_registry import register_template


@register_template("class.bundle.created")
class ClassBundleCreatedTemplate(BaseNotificationTemplate):
    """Notification when class bundle is created for client."""
    
    def get_title(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "Class Bundle")
        return f"New Class Bundle: {bundle_name}"
    
    def get_message(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "class bundle")
        total_price = payload.get("total_price", "0.00")
        number_of_classes = payload.get("number_of_classes", 0)
        message = (
            f"A new class bundle '{bundle_name}' with {number_of_classes} classes "
            f"has been created for you. Total price: ${total_price}. "
        )
        deposit_required = payload.get("deposit_required")
        if deposit_required:
            message += f"Deposit required: ${deposit_required}. "
        message += "You can view and pay for your bundle in your account."
        return message
    
    def get_link(self, payload: dict) -> str:
        bundle_id = payload.get("bundle_id")
        return f"/classes/{bundle_id}" if bundle_id else "/classes"


@register_template("class.bundle.deposit_paid")
class ClassDepositPaidTemplate(BaseNotificationTemplate):
    """Notification when class deposit is paid."""
    
    def get_title(self, payload: dict) -> str:
        amount = payload.get("amount", "0.00")
        return f"Class Deposit Paid - ${amount}"
    
    def get_message(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "class bundle")
        amount = payload.get("amount", "0.00")
        balance_remaining = payload.get("balance_remaining", "0.00")
        message = (
            f"Your deposit of ${amount} for '{bundle_name}' has been received. "
        )
        if float(balance_remaining) > 0:
            message += f"Balance remaining: ${balance_remaining}. "
        message += "Your classes are now active!"
        return message
    
    def get_link(self, payload: dict) -> str:
        bundle_id = payload.get("bundle_id")
        return f"/classes/{bundle_id}" if bundle_id else "/classes"


@register_template("class.installment.due")
class ClassInstallmentDueTemplate(BaseNotificationTemplate):
    """Notification when class installment is due."""
    
    def get_title(self, payload: dict) -> str:
        amount = payload.get("amount", "0.00")
        return f"Class Installment Due - ${amount}"
    
    def get_message(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "class bundle")
        amount = payload.get("amount", "0.00")
        due_date = payload.get("due_date", "")
        installment_number = payload.get("installment_number", 1)
        total_installments = payload.get("total_installments", 1)
        
        message = (
            f"Your installment payment #{installment_number} of {total_installments} "
            f"for ${amount} is due"
        )
        if due_date:
            message += f" by {due_date}"
        message += f" for '{bundle_name}'. Please make your payment to continue."
        return message
    
    def get_link(self, payload: dict) -> str:
        bundle_id = payload.get("bundle_id")
        installment_id = payload.get("installment_id")
        if installment_id:
            return f"/classes/{bundle_id}/installments/{installment_id}/pay"
        return f"/classes/{bundle_id}/pay" if bundle_id else "/classes"


@register_template("class.bundle.completed")
class ClassBundleCompletedTemplate(BaseNotificationTemplate):
    """Notification when class bundle is completed."""
    
    def get_title(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "Class Bundle")
        return f"🎓 Class Bundle Completed: {bundle_name}"
    
    def get_message(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "class bundle")
        number_of_classes = payload.get("number_of_classes", 0)
        return (
            f"Congratulations! You've completed your '{bundle_name}' bundle "
            f"with all {number_of_classes} classes. Thank you for your participation!"
        )
    
    def get_link(self, payload: dict) -> str:
        bundle_id = payload.get("bundle_id")
        return f"/classes/{bundle_id}" if bundle_id else "/classes"


@register_template("class.message.received")
class ClassMessageReceivedTemplate(BaseNotificationTemplate):
    """Notification when message is received in class thread."""
    
    def get_title(self, payload: dict) -> str:
        sender_name = payload.get("sender_name", "Someone")
        return f"New Message in Class Thread from {sender_name}"
    
    def get_message(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "your class")
        sender_name = payload.get("sender_name", "Someone")
        preview = payload.get("message_preview", "")
        if preview and len(preview) > 100:
            preview = preview[:100] + "..."
        message = f"You received a new message from {sender_name} regarding '{bundle_name}'. "
        if preview:
            message += f'"{preview}"'
        return message
    
    def get_link(self, payload: dict) -> str:
        thread_id = payload.get("thread_id")
        bundle_id = payload.get("bundle_id")
        if thread_id:
            return f"/communications/threads/{thread_id}"
        return f"/classes/{bundle_id}/messages" if bundle_id else "/communications"


@register_template("class.ticket.created")
class ClassTicketCreatedTemplate(BaseNotificationTemplate):
    """Notification when ticket is created for class."""
    
    def get_title(self, payload: dict) -> str:
        ticket_subject = payload.get("subject", "Support Ticket")
        return f"New Support Ticket: {ticket_subject}"
    
    def get_message(self, payload: dict) -> str:
        bundle_name = payload.get("bundle_name", "your class")
        ticket_subject = payload.get("subject", "support ticket")
        message = (
            f"A new support ticket '{ticket_subject}' has been created for "
            f"'{bundle_name}'. Our team will respond as soon as possible."
        )
        return message
    
    def get_link(self, payload: dict) -> str:
        ticket_id = payload.get("ticket_id")
        return f"/tickets/{ticket_id}" if ticket_id else "/tickets"

