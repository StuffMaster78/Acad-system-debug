from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from websites.models import Website
from orders.models import Order, Dispute
from tickets.models import Ticket
from django.core.exceptions import ValidationError

User = get_user_model()


class SupportProfile(models.Model):
    """
    Profile for support staff.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="support_profile",
        limit_choices_to={"role": "support"},
        help_text="The user associated with this support profile."
    )
    name = models.CharField(
        max_length=255,
        help_text="Full name of the support staff."
    )
    registration_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique support staff registration ID (e.g., Support #12345)."
    )
    email = models.EmailField(unique=True, help_text="Support staff's email address.")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Support staff's phone number."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="support_staff",
        help_text="The website the support staff is associated with."
    )
    last_logged_in = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The last time the support staff logged in."
    )
    orders_handled = models.PositiveIntegerField(
        default=0,
        help_text="Total number of orders managed by this support staff."
    )
    disputes_handled = models.PositiveIntegerField(
        default=0,
        help_text="Total number of disputes resolved by this support staff."
    )
    tickets_handled = models.PositiveIntegerField(
        default=0,
        help_text="Total number of tickets resolved by this support staff."
    )

    def __str__(self):
        return f"{self.name} (Support Profile: {self.user.username}, {self.registration_id})"


    def can_accept_tasks(self):
        """
        Check if the support staff can accept tasks.
        """
        if self.is_suspended():
            return False
        return True

    def is_suspended(self):
        """
        Check if the support staff is currently suspended.
        """
        return self.action_logs.filter(action="suspension", suspension_end_date__gte=now()).exists()

    def clean(self):
        """
        Override the clean method to enforce business rules.
        """
        if not self.is_active and self.is_suspended():
            raise ValidationError("Inactive or suspended support staff cannot accept tasks.")
        super().clean()

    def assign_bulk_tickets(self, tickets):
        """
        Assign multiple tickets to this support staff.
        """
        for ticket in tickets:
            TicketAssignment.assign_ticket(ticket, self)
        return f"Assigned {len(tickets)} tickets to {self.name}."

class SupportActionLog(models.Model):
    """
    Logs actions performed by support staff.
    """
    support_staff = models.ForeignKey(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="action_logs",
        help_text="The support staff who performed this action."
    )
    action = models.CharField(
        max_length=255,
        help_text="Description of the action performed (e.g., 'Assigned Order', 'Resolved Dispute')."
    )
    related_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_actions",
        help_text="The order associated with this action, if applicable."
    )
    related_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_actions",
        help_text="The ticket associated with this action, if applicable."
    )
    related_dispute = models.ForeignKey(
        Dispute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_actions",
        help_text="The dispute associated with this action, if applicable."
    )
    is_suspended = models.BooleanField(
        default=False,
        help_text="Indicates whether the support staff is suspended."
    )
    suspension_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for suspending the support staff."
    )
    suspension_start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time when the suspension started."
    )
    suspension_end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time when the suspension will end, if applicable."
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the action was performed.")

    def __str__(self):
        return f"Action by {self.support_staff.name}: {self.action} at {self.timestamp}"

    def suspend(self, reason, start_date=None, end_date=None):
        """
        Suspend the support staff with a reason and optional start/end dates.
        """
        self.is_suspended = True
        self.suspension_reason = reason
        self.suspension_start_date = start_date or now()
        self.suspension_end_date = end_date
        self.save()

    def lift_suspension(self):
        """
        Lift the suspension for the support staff.
        """
        self.is_suspended = False
        self.suspension_reason = None
        self.suspension_start_date = None
        self.suspension_end_date = None
        self.save()
class SupportActivityLog(models.Model):
    """
    Logs all activities of support staff.
    """
    support_staff = models.ForeignKey(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        help_text="The support staff whose activity is being logged."
    )
    activity = models.TextField(
        help_text="Detailed description of the activity performed."
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the activity.")

    def __str__(self):
        return f"Activity by {self.support_staff.name} at {self.timestamp}"


class DisputeResolutionLog(models.Model):
    """
    Tracks details of dispute resolutions handled by support staff.
    """
    dispute = models.OneToOneField(
        Dispute,
        on_delete=models.CASCADE,
        related_name="resolution_log",
        help_text="The dispute being resolved."
    )
    resolved_by = models.ForeignKey(
        SupportProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dispute_resolutions",
        help_text="The support staff resolving the dispute."
    )
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Details of the resolution."
    )
    resolved_at = models.DateTimeField(
        default=now,
        help_text="Timestamp when the dispute was resolved."
    )

    def __str__(self):
        return f"Dispute {self.dispute.id} resolved by {self.resolved_by.name}"


class TicketAssignment(models.Model):
    """
    Tracks tickets assigned to support staff.
    """
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name="assignment",
        help_text="The ticket being assigned."
    )
    assigned_to = models.ForeignKey(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="assigned_tickets",
        help_text="The support staff assigned to this ticket."
    )
    assigned_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the ticket was assigned.")
    completed_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when the ticket was resolved.")

    def __str__(self):
        return f"Ticket {self.ticket.id} assigned to {self.assigned_to.name}"
    
    @staticmethod
    def assign_ticket(ticket, support_staff):
        """
        Assign a ticket to support staff.
        """
        if not support_staff.can_accept_tasks():
            raise ValidationError(f"{support_staff.name} is suspended or unable to take on new tasks.")
        
        assignment = TicketAssignment.objects.create(ticket=ticket, assigned_to=support_staff)
        support_staff.tickets_handled += 1
        support_staff.save()
        return assignment
    
    def resolve_ticket(self):
        """
        Mark a ticket as resolved.
        """
        self.completed_at = now()
        self.save()
        self.assigned_to.tickets_handled += 1
        self.assigned_to.save()
        return self.ticket

class SupportAvailability(models.Model):
    support_staff = models.ForeignKey(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="availability",
        help_text="The support staff whose availability is being tracked."
    )
    start_time = models.DateTimeField(help_text="Shift start time.")
    end_time = models.DateTimeField(help_text="Shift end time.")
    is_recurring = models.BooleanField(
        default=False,
        help_text="Indicates if this availability is recurring (e.g., daily, weekly)."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the support staff is currently available."
    )

    def __str__(self):
        return f"{self.support_staff.name} availability ({self.start_time} - {self.end_time})"

    def clean(self):
        """
        Validate start_time and end_time.
        """
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        super().clean() 

class SupportPerformance(models.Model):
    support_staff = models.OneToOneField(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="performance",
        help_text="The support staff whose performance is being tracked."
    )
    average_response_time = models.DurationField(
        blank=True,
        null=True,
        help_text="Average time taken to respond to tickets or disputes."
    )
    average_resolution_time = models.DurationField(
        blank=True,
        null=True,
        help_text="Average time taken to resolve tickets or disputes."
    )
    total_tickets_resolved = models.PositiveIntegerField(
        default=0,
        help_text="Total number of tickets resolved by the support staff."
    )
    total_disputes_resolved = models.PositiveIntegerField(
        default=0,
        help_text="Total number of disputes resolved by the support staff."
    )

    def __str__(self):
        return f"Performance for {self.support_staff.name}"
    

class SupportNotification(models.Model):

    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level of the notification."
    )
    support_staff = models.ForeignKey(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The support staff receiving the notification."
    )
    message = models.TextField(help_text="Notification message.")
    related_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Related ticket, if applicable."
    )
    related_dispute = models.ForeignKey(
        Dispute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Related dispute, if applicable."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the notification was created.")
    is_read = models.BooleanField(default=False, help_text="Indicates whether the notification has been read.")

    def __str__(self):
        return f"Notification for {self.support_staff.name}: {self.message[:30]}"
    
    @staticmethod
    def notify_staff(support_staff, message, priority="medium", related_ticket=None, related_dispute=None):
        """
        Create a notification for the support staff with a specified priority.
        """
        notification = SupportNotification.objects.create(
            support_staff=support_staff,
            message=message,
            priority=priority,
            related_ticket=related_ticket,
            related_dispute=related_dispute,
        )
        return notification

class EscalationLog(models.Model):
    escalated_by = models.ForeignKey(
        SupportProfile,
        on_delete=models.CASCADE,
        related_name="escalation_logs",
        help_text="The support staff escalating the issue."
    )
    escalated_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="escalated_issues",
        help_text="The user (admin/superadmin) to whom the issue is escalated."
    )
    related_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalation_logs",
        help_text="Related ticket, if applicable."
    )
    related_dispute = models.ForeignKey(
        Dispute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="escalation_logs",
        help_text="Related dispute, if applicable."
    )
    reason = models.TextField(help_text="Reason for escalation.")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the escalation.")

    def __str__(self):
        return f"Escalation by {self.escalated_by.name} to {self.escalated_to.username}"
    
    @staticmethod
    def escalate_issue(issue_type, issue, escalated_by, escalated_to, reason):
        """
        Log an escalation for a ticket or dispute.
        """
        escalation = EscalationLog.objects.create(
            escalated_by=escalated_by,
            escalated_to=escalated_to,
            related_ticket=issue if issue_type == "ticket" else None,
            related_dispute=issue if issue_type == "dispute" else None,
            reason=reason,
        )
        return escalation
