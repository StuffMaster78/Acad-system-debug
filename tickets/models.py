        
from django.db import models
from django.conf import settings
from websites.models import Website

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('awaiting_response', 'Awaiting Response'),
        ('escalated', 'Escalated'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', 'General Inquiry'),
        ('payment', 'Payment Issues'),
        ('technical', 'Technical Support'),
        ('feedback', 'Feedback'),
        ('order', 'Order Issues'),
        ('other', 'Other reasons'),
    ]

    title = models.CharField(max_length=255, help_text="Title of the ticket.")
    description = models.TextField(help_text="Detailed description of the issue.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets_created",
        help_text="The user who created this ticket.",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_assigned",
        help_text="The admin/support user assigned to this ticket.",
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
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the ticket.",
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of the ticket.",
    )
    is_escalated = models.BooleanField(default=False, help_text="Indicates if the ticket is escalated.")
    resolution_time = models.DateTimeField(null=True, blank=True, help_text="When the ticket was resolved.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the ticket was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the ticket was last updated.")

    def __str__(self):
        return f"{self.title} ({self.status}) - {self.priority}"

    class Meta:
        ordering = ['-created_at']

class TicketMessage(models.Model):
    """
    A Model that stores and handles tickets within a message
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
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


class TicketLog(models.Model):
    """
    Logs all the tickets raised for the respective websites.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="logs",
        help_text="The ticket this log entry belongs to.",
    )
    action = models.CharField(max_length=255, help_text="Description of the action taken.")
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who performed this action.",
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When this action was performed.")

    def __str__(self):
        return f"Log for {self.ticket.title} - {self.action}"

    class Meta:
        ordering = ['-timestamp']


class TicketStatistics(models.Model):
    """
    Tracks all the tickets for the respective websites
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="ticket_stats"
    )
    total_tickets = models.IntegerField(
        default=0,
        help_text="Total number of tickets."
    )
    resolved_tickets = models.IntegerField(
        default=0,
        help_text="Total number of resolved tickets."
    )
    average_resolution_time = models.FloatField(
        default=0.0,
        help_text="Average resolution time in hours."
    )
    created_at = models.DateField(
        auto_now_add=True,
        help_text="Date of the statistic."
    )

    def __str__(self):
        return f"Stats for {self.website} - {self.created_at}"