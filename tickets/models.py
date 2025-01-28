from django.db import models
from django.conf import settings
from websites.models import Website

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('awaiting_response', 'Awaiting Response'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('payment', 'Payment Issues'),
        ('technical', 'Technical Support'),
        ('feedback', 'Feedback'),
        ('order', 'Order Issues'),
    ]

    title = models.CharField(max_length=255, help_text="Title of the ticket.")
    description = models.TextField(help_text="Detailed description of the issue.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets_created",
        help_text="The user who created this ticket.",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_received",
        help_text="The user this ticket is directed to (admin/support only).",
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="tickets",
        help_text="The website this ticket is associated with.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Current status of the ticket.",
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of the ticket.",
    )
    is_escalated = models.BooleanField(default=False, help_text="Indicates if the ticket is escalated.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the ticket was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the ticket was last updated.")

    def __str__(self):
        return f"{self.title} ({self.status})"

    class Meta:
        ordering = ['-created_at']

class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="The ticket this message belongs to.",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ticket_messages_sent",
        help_text="The user who sent this message.",
    )
    message = models.TextField(help_text="The content of the message.")
    is_internal = models.BooleanField(
        default=False,
        help_text="Indicates if this is an internal message (admins/support only).",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this message was sent.")

    def __str__(self):
        return f"Message by {self.sender} on {self.ticket.title}"

    class Meta:
        ordering = ['created_at']