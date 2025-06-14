from django.utils.text import slugify


def ticket_attachment_upload_path(instance, filename):
    from tickets.models import TicketAttachment
    ext = filename.split('.')[-1]
    ticket_id = instance.ticket.id
    truncated_title = slugify(instance.ticket.title)[:20]
    return f"ticket_attachments/Ticket_{ticket_id}-{truncated_title}.{ext}"