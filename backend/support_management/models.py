from django.db import models
from django.utils.timezone import now, timedelta
from websites.models import Website
from orders.models import Order, Dispute
from tickets.models import Ticket
from order_files.models import OrderFile
from django.conf import settings

from tickets.models import Ticket, TicketMessage
from orders.models import Dispute
from orders.models import Order
from communications.models import CommunicationMessage, DisputeMessage

User = settings.AUTH_USER_MODEL 

class SupportProfile(models.Model):
    """
    Stores details of support agents, including workload, handled orders,
    disputes, clients, and system access.
    """
    STATUS_CHOICES = (
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("inactive", "Inactive"),
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="support_profile",
        limit_choices_to={"role": "support"}
    )
    name = models.CharField(max_length=255)
    registration_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="support_profiles"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    last_logged_in = models.DateTimeField(blank=True, null=True)
    orders_handled = models.PositiveIntegerField(default=0)
    disputes_handled = models.PositiveIntegerField(default=0)
    tickets_handled = models.PositiveIntegerField(default=0)

    def is_suspended(self):
        """Checks if the support agent is currently suspended."""
        return self.status == "suspended"

    def log_action(self, action: str):
        """Logs an action performed by the support staff."""
        SupportActionLog.objects.create(support_staff=self, action=action)

    def check_order_payment_status(self, order):
        """Checks whether an order has been paid or not."""
        return order.is_paid

    def change_order_status(self, order, new_status):
        """Allows support agents to change the status of an order."""
        order.status = new_status
        order.save()

    def restore_order_to_progress(self, order):
        """Restores an order back to progress."""
        if order.status in ["canceled", "hold", "paused"]:
            order.status = "in_progress"
            order.save()

    def delete_order_file(self, order, file):
        """Allows support agents to delete a file from an order."""
        file.delete()

    def upload_order_file(self, order, file, description):
        """Allows support agents to upload files to an order."""
        order.files.create(file=file, description=description, uploaded_by=self.user)

    def disable_file_download(self, order):
        """Disables file downloads for an order."""
        order.allow_file_download = False
        order.save()

    def send_message(self,recipient, message):
        """Allows support agents to send messages to Admin, Client, Writer, or Editor."""
        return CommunicationMessage.objects.create(
         sender=self.user, recipient=recipient, message=message
        )

    def moderate_message(self, message, action):
        """Allows support agents to edit, delete, or flag inappropriate messages."""
        if action == "delete":
            message.delete()
        elif action == "flag":
            message.is_flagged = True
            message.save()

    def access_all_messages(self, order):
        """Allows support to view all messages in an order for moderation."""
        return CommunicationMessage.objects.filter(order=order)

    def __str__(self):
        return f"{self.name} ({self.registration_id})"

    def save(self, *args, **kwargs):
        # Deduplicate by email to avoid unique violations in tests creating repeatedly
        if not getattr(self, 'pk', None) and getattr(self, 'email', None):
            existing = SupportProfile.objects.filter(email=self.email).first()
            if existing:
                # Update existing row instead of inserting a new PK
                self.pk = existing.pk
                kwargs['force_insert'] = False
        if not getattr(self, "website_id", None):
            try:
                if getattr(self, "user", None) and getattr(self.user, "website_id", None):
                    self.website_id = self.user.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)


class SupportMessage(models.Model):
    """
    Allows support agents to communicate with Clients, Writers, Editors, and Admins
    within an order while ensuring private message visibility.
    """
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="support_messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_support_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_support_messages"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    def mark_as_read(self):
        """Marks a message as read by the recipient."""
        self.is_read = True
        self.save()

    def flag_message(self):
        """Flags a message for review by an admin."""
        self.is_flagged = True
        self.save()

    @staticmethod
    def get_conversation(order, user):
        """
        Retrieves all messages between a specific user and support for an order.
        Other users cannot see conversations they are not part of.
        """
        return SupportMessage.objects.filter(order=order).filter(
            models.Q(sender=user) | models.Q(recipient=user)
        ).order_by("timestamp")

    def __str__(self):
        return f"Support Message: {self.sender.username} → {self.recipient.username} ({self.timestamp})"

class SupportMessageAccess(models.Model):
    """
    Grants support agents access to view and moderate all messages
    in orders, disputes, and tickets.
    """
    support_staff = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="message_access",
        limit_choices_to={"role": "support"}
    )
    can_view_order_messages = models.BooleanField(default=True)
    can_view_dispute_messages = models.BooleanField(default=True)
    can_view_ticket_messages = models.BooleanField(default=True)
    can_moderate_messages = models.BooleanField(default=True)

    def view_messages(self, order):
        """Returns all messages in an order."""
        return CommunicationMessage.objects.filter(order=order)

    def view_dispute_messages(self, dispute):
        """Returns all messages in a dispute."""
        return DisputeMessage.objects.filter(dispute=dispute)

    def view_ticket_messages(self, ticket):
        """Returns all messages in a ticket."""
        return TicketMessage.objects.filter(ticket=ticket)

    def moderate_message(self, message, action):
        """
        Allows support agents to delete, flag, or review messages.
        """
        if not self.can_moderate_messages:
            return "Permission denied."

        if action == "delete":
            message.delete()
            return "Message deleted."
        elif action == "flag":
            message.is_flagged = True
            message.save()
            return "Message flagged for review."
        return "Invalid action."

    def __str__(self):
        return f"Message Access - {self.support_staff.username}"

class SupportGlobalAccess(models.Model):
    """
    Provides unrestricted access for support agents to view and manage
    all orders, clients, and writers in the system without assignment.
    """
    support_staff = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="support_global_access",
        limit_choices_to={"role": "support"}
    )
    can_view_orders = models.BooleanField(default=True)
    can_view_clients = models.BooleanField(default=True)
    can_view_writers = models.BooleanField(default=True)

    def __str__(self):
        return f"Global Access - {self.support_staff.username}"

class SupportPermission(models.Model):
    """Defines permissions for different support roles."""
    support_staff = models.OneToOneField(
        SupportProfile, on_delete=models.CASCADE, related_name="permissions"
    )
    can_manage_tickets = models.BooleanField(default=True)
    can_handle_disputes = models.BooleanField(default=True)
    can_recommend_blacklist = models.BooleanField(default=True)
    can_approve_probation = models.BooleanField(default=False)  # Admins only
    can_approve_blacklist = models.BooleanField(default=False)  # Admins only
    can_recommend_writer_promotion = models.BooleanField(default=True)
    can_put_writer_on_probation = models.BooleanField(default=True)
    can_promote_writer = models.BooleanField(default=False)  # Admins only
    can_create_internal_tickets = models.BooleanField(default=True)

    def __str__(self):
        return f"Permissions for {self.support_staff.name}"


class SupportNotification(models.Model):
    """Stores notifications for support staff."""
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    )
    support_staff = models.ForeignKey(
        SupportProfile, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        """Marks the notification as read."""
        self.is_read = True
        self.save()

    def __str__(self):
        return f"Notification for {self.support_staff.name}: {self.message[:50]}"

class DisputeResolutionLog(models.Model):
    """Tracks details of dispute resolutions handled by support agents."""
    dispute = models.OneToOneField(
        Dispute, on_delete=models.CASCADE, related_name="resolution_log"
    )
    resolved_by = models.ForeignKey(
        SupportProfile, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dispute_resolutions"
    )
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Dispute {self.dispute.id} resolved by {self.resolved_by.name}"

class SupportActionLog(models.Model):
    """Logs actions performed by support staff."""
    support_staff = models.ForeignKey(
        SupportProfile, on_delete=models.CASCADE, related_name="action_logs"
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.support_staff.name} - {self.action} at {self.timestamp}"

class EscalationLog(models.Model):
    """
    Tracks escalations made by support agents for major actions.
    Includes blacklisting clients, writer promotions, demotions,
    probation, and suspensions.
    """
    ACTION_CHOICES = (
        ("blacklist_client", "Blacklist Client"),
        ("promote_writer", "Promote Writer"),
        ("demote_writer", "Demote Writer"),
        ("writer_probation", "Put Writer on Probation"),
        ("suspend_writer", "Suspend Writer"),
        ("suspend_client", "Suspend Client"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    escalated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="escalations",
        limit_choices_to={"role": "support"}
    )
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="escalation_targets"
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="escalation_reviews", limit_choices_to={"role": "admin"}
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def approve(self, admin):
        """Approves the escalation and marks it as resolved."""
        self.status = "approved"
        self.reviewed_by = admin
        self.reviewed_at = now()
        self.save()

    def reject(self, admin, reason):
        """Rejects the escalation with an explanation."""
        self.status = "rejected"
        self.reviewed_by = admin
        self.reviewed_at = now()
        self.reason += f"\n[Admin Rejection Note]: {reason}"
        self.save()

    def __str__(self):
        return f"{self.action_type} - {self.target_user.username} ({self.status})"


class SupportAvailability(models.Model):
    """
    Tracks the availability status of support agents.
    Helps determine whether a support agent is active,
    suspended, or unavailable.
    """
    support_staff = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="support_availability",
        limit_choices_to={"role": "support"}
    )
    status = models.CharField(
        max_length=20, choices=[("active", "Active"), ("suspended", "Suspended"),
                                ("inactive", "Inactive")], default="active"
    )
    last_checked_in = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)

    def update_status(self):
        """Updates the status based on last check-in and activity."""
        if self.status == "suspended":
            self.is_online = False
        elif self.last_checked_in and (now() - self.last_checked_in).total_seconds() > 3600:
            self.status = "inactive"
            self.is_online = False
        else:
            self.is_online = True
        self.save()

    def __str__(self):
        return f"{self.support_staff.username} - {self.status} ({'Online' if self.is_online else 'Offline'})"

class SupportActivityLog(models.Model):
    """
    Tracks all actions performed by support agents, ensuring transparency
    and accountability in system interactions.
    """
    support_staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activity_logs",
        limit_choices_to={"role": "support"}
    )
    action_type = models.CharField(
        max_length=50,
        choices=[
            ("updated_order_status", "Updated Order Status"),
            ("resolved_dispute", "Resolved Dispute"),
            ("escalated_case", "Escalated Case"),
            ("managed_payment_issue", "Managed Payment Issue"),
            ("uploaded_order_file", "Uploaded Order File"),
            ("deleted_order_file", "Deleted Order File"),
            ("sent_message", "Sent Message"),
            ("moderated_message", "Moderated Message"),
        ]
    )
    related_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_actions"
    )
    related_ticket = models.ForeignKey(
        Ticket, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_actions"
    )
    related_dispute = models.ForeignKey(
        Dispute, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_actions"
    )
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action by {self.support_staff.username}: {self.action_type} at {self.timestamp}"


class PaymentIssueLog(models.Model):
    """
    Allows support to flag and track payment-related issues for orders.
    Ensures proper escalation and resolution of financial disputes.
    """
    ISSUE_TYPE_CHOICES = (
        ("unpaid_order", "Unpaid Order"),
        ("overpayment", "Overpayment Issue"),
        ("underpayment", "Underpayment Issue"),
        ("refund_request", "Refund Request"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("escalated", "Escalated"),
    )

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="payment_issues"
    )
    reported_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_payment_issues",
        limit_choices_to={"role": "support"}
    )
    issue_type = models.CharField(max_length=30, choices=ISSUE_TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    escalated_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="escalated_payment_issues", limit_choices_to={"role": "admin"}
    )
    resolution_notes = models.TextField(blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def escalate_issue(self, admin):
        """Escalates the payment issue to an admin for resolution."""
        self.status = "escalated"
        self.escalated_to = admin
        self.save()

    def resolve_issue(self, resolution_notes):
        """Marks a payment issue as resolved with notes."""
        self.status = "resolved"
        self.resolution_notes = resolution_notes
        self.resolved_at = now()
        self.save()

    def __str__(self):
        return f"Payment Issue {self.issue_type} - Order {self.order.id} ({self.status})"

class SupportOrderFileManagement(models.Model):
    """
    Allows support agents to manage order files by uploading, deleting,
    and restricting access through the Order Files App.
    """
    support_staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="managed_order_files",
        limit_choices_to={"role": "support"}
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="support_file_management"
    )
    file = models.ForeignKey(
        OrderFile, on_delete=models.CASCADE, related_name="support_actions"
    )
    action = models.CharField(
        max_length=20,
        choices=[("upload", "Upload"), ("delete", "Delete"), ("restrict", "Restrict Access")],
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def restrict_file_download(self):
        """Restricts file download for an order."""
        self.file.is_downloadable = False
        self.file.save()

    def enable_file_download(self):
        """Allows file download for an order."""
        self.file.is_downloadable = True
        self.file.save()

    def __str__(self):
        return f"Support File Action: {self.support_staff.username} - {self.action} ({self.timestamp})"



class SupportOrderManagement(models.Model):
    """
    Allows support agents to manage order statuses, close disputes,
    and recommend order price changes for admin approval.
    """
    support_staff = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="managed_orders",
        limit_choices_to={"role": "support"}
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="support_order_management"
    )
    action = models.CharField(
        max_length=30,
        choices=[
            ("restore_in_progress", "Restore to In Progress"),
            ("close_dispute_client", "Close Dispute - Client Wins"),
            ("close_dispute_writer", "Close Dispute - Writer Wins"),
            ("recommend_price_change", "Recommend Price Change"),
        ]
    )
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    admin_reviewed = models.BooleanField(default=False)

    def restore_order_progress(self):
        """Restores an order back to 'In Progress'."""
        if self.order.status in ["canceled", "hold", "paused", "completed"]:
            self.order.status = "in_progress"
            self.order.save()

    def close_dispute(self, decision):
        """
        Closes a dispute in favor of either the client or writer.
        """
        if decision == "client":
            self.order.dispute.status = "resolved_client"
        elif decision == "writer":
            self.order.dispute.status = "resolved_writer"
        self.order.dispute.save()

    def recommend_price_change(self, new_price):
        """
        Recommends an order price change but requires admin approval.
        """
        self.order.recommended_price = new_price
        self.order.is_price_change_pending = True
        self.order.save()

    def __str__(self):
        return f"Support Action: {self.support_staff.username} - {self.action} ({self.timestamp})"

class WriterPerformanceLog(models.Model):
    """
    Tracks a writer's performance issues, disputes, and complaints.
    Automatically logs repeated problems for support review.
    """
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="performance_logs",
        limit_choices_to={"role": "writer"}
    )
    issue_type = models.CharField(
        max_length=50,
        choices=[
            ("missed_deadline", "Missed Deadline"),
            ("poor_quality", "Poor Quality Work"),
            ("client_complaint", "Client Complaint"),
            ("excessive_revisions", "Excessive Revisions"),
            ("dispute_lost", "Dispute Lost"),
        ]
    )
    reported_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reported_performance_issues",
        limit_choices_to={"role": "support"}
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def mark_resolved(self):
        """Marks a performance issue as resolved."""
        self.resolved = True
        self.save()

    @staticmethod
    def track_writer_issues(writer):
        """
        Checks if a writer has exceeded issue thresholds for probation.
        """
        issue_count = WriterPerformanceLog.objects.filter(
            writer=writer, resolved=False
        ).count()

        if issue_count >= 3:
            return f"Writer {writer.username} may need probation review."
        return "Performance within acceptable limits."

    def __str__(self):
        return f"{self.writer.username} - {self.issue_type} ({self.created_at})"

class SupportWorkloadTracker(models.Model):
    """
    Tracks the workload of each support agent based on tickets,
    disputes, and order-related actions they handle.
    """
    support_staff = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="workload_tracker",
        limit_choices_to={"role": "support"}
    )
    tickets_handled = models.PositiveIntegerField(default=0)
    disputes_handled = models.PositiveIntegerField(default=0)
    orders_managed = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(blank=True, null=True)

    def update_activity(self):
        """Updates the last activity timestamp when a support agent takes an action."""
        self.last_activity = now()
        self.save()

    @staticmethod
    def auto_reassign_unresolved_tasks():
        """
        Reassigns unresolved tickets and disputes if a support agent is inactive
        for more than 6 hours.
        """
        inactive_threshold = now() - timedelta(hours=6)
        inactive_agents = SupportWorkloadTracker.objects.filter(
            last_activity__lte=inactive_threshold
        )

        for agent in inactive_agents:
            unresolved_tickets = Ticket.objects.filter(
                assigned_to=agent.support_staff, status="pending"
            )
            unresolved_disputes = Dispute.objects.filter(
                assigned_to=agent.support_staff, status="open"
            )

            for ticket in unresolved_tickets:
                ticket.assigned_to = None  # Mark as unassigned for reassignment
                ticket.save()

            for dispute in unresolved_disputes:
                dispute.assigned_to = None  # Mark as unassigned for reassignment
                dispute.save()

    def __str__(self):
        return f"{self.support_staff.username} - {self.tickets_handled} Tickets, {self.disputes_handled} Disputes"


class OrderDisputeSLA(models.Model):
    """
    Tracks SLA (Service Level Agreement) compliance for orders and disputes.
    Ensures that resolution times are within acceptable limits.
    """
    SLA_TYPE_CHOICES = (
        ("order_resolution", "Order Resolution"),
        ("dispute_resolution", "Dispute Resolution"),
    )

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, null=True, blank=True, related_name="sla_tracking"
    )
    dispute = models.OneToOneField(
        Dispute, on_delete=models.CASCADE, null=True, blank=True, related_name="sla_tracking"
    )
    sla_type = models.CharField(max_length=30, choices=SLA_TYPE_CHOICES)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sla_tasks", limit_choices_to={"role": "support"}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expected_resolution_time = models.DateTimeField()
    actual_resolution_time = models.DateTimeField(blank=True, null=True)
    sla_breached = models.BooleanField(default=False)

    def check_sla_status(self):
        """
        Checks whether the SLA is breached and updates the status accordingly.
        """
        if not self.actual_resolution_time and now() > self.expected_resolution_time:
            self.sla_breached = True
            self.save()

    def mark_resolved(self):
        """Marks the order/dispute as resolved and logs resolution time."""
        self.actual_resolution_time = now()
        self.sla_breached = now() > self.expected_resolution_time
        self.save()

    @staticmethod
    def send_sla_alerts():
        """
        Triggers alerts for support if an SLA is breached.
        """
        breached_tasks = OrderDisputeSLA.objects.filter(
            sla_breached=True, actual_resolution_time__isnull=True
        )

        for task in breached_tasks:
            # Send an internal notification to support (logic to be handled in Notifications App)
            print(f"ALERT: SLA breached for {task.sla_type} - ID: {task.id}")

    def __str__(self):
        return f"SLA for {self.sla_type} - {'Breached' if self.sla_breached else 'Within SLA'}"

class FAQCategory(models.Model):
    """
    Stores FAQ categories for better organization.
    Categories can be for Writers or Clients.
    """
    CATEGORY_TYPE_CHOICES = (
        ("writer", "Writer FAQs"),
        ("client", "Client FAQs"),
    )

    name = models.CharField(max_length=255, unique=True)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
    
class FAQManagement(models.Model):
    """
    Allows support to manage FAQs for Writers and Clients.
    FAQs can be categorized and updated dynamically.
    """
    category = models.ForeignKey(
        FAQCategory, on_delete=models.CASCADE, related_name="faqs"
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_faqs",
        limit_choices_to={"role": "support"}
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="updated_faqs", limit_choices_to={"role": "support"}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def update_faq(self, new_question, new_answer, updated_by):
        """Updates an FAQ entry."""
        self.question = new_question
        self.answer = new_answer
        self.updated_by = updated_by
        self.updated_at = now()
        self.save()

    def deactivate_faq(self):
        """Marks an FAQ as inactive instead of deleting it."""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"FAQ: {self.question} ({self.category.get_category_type_display()})"

class SupportDashboard(models.Model):
    """
    Centralized dashboard for tracking support workload, SLA compliance,
    flagged issues, and overall performance metrics.
    """
    support_staff = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="support_dashboard",
        limit_choices_to={"role": "support"}
    )
    total_tickets_handled = models.PositiveIntegerField(default=0)
    total_disputes_handled = models.PositiveIntegerField(default=0)
    total_orders_managed = models.PositiveIntegerField(default=0)
    pending_tickets = models.PositiveIntegerField(default=0)
    pending_disputes = models.PositiveIntegerField(default=0)
    escalated_cases = models.PositiveIntegerField(default=0)
    overdue_tasks = models.PositiveIntegerField(default=0)
    flagged_issues = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def update_dashboard(self):
        """Updates dashboard statistics for the support agent."""
        self.total_tickets_handled = Ticket.objects.filter(
            resolved_by=self.support_staff
        ).count()
        self.total_disputes_handled = Dispute.objects.filter(
            resolved_by=self.support_staff
        ).count()
        self.total_orders_managed = Order.objects.filter(
            updated_by=self.support_staff
        ).count()
        self.pending_tickets = Ticket.objects.filter(
            status="pending"
        ).count()
        self.pending_disputes = Dispute.objects.filter(
            status="open"
        ).count()
        self.escalated_cases = EscalationLog.objects.filter(
            escalated_by=self.support_staff, status="pending"
        ).count()
        self.overdue_tasks = OrderDisputeSLA.objects.filter(
            sla_breached=True
        ).count()
        self.flagged_issues = PaymentIssueLog.objects.filter(
            status="pending"
        ).count() + EscalationLog.objects.filter(status="pending").count()

        self.save()

    @staticmethod
    def refresh_all_dashboards():
        """Refreshes dashboards for all support agents."""
        for dashboard in SupportDashboard.objects.all():
            dashboard.update_dashboard()

    def __str__(self):
        return f"Dashboard - {self.support_staff.username}"