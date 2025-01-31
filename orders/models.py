from django.db import models
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal
from pricing_configs.models import PricingConfiguration
from order_configs.models import WriterDeadlineConfig
from discounts.models import Discount
from users.models import User
from core.models.base import WebsiteSpecificBaseModel
from django.core.mail import send_mail
from django.apps import apps 

STATUS_CHOICES = [
    ('unpaid', 'Unpaid'),
    ('pending', 'Pending'),
    ('on_hold', 'On Hold'),
    ('available', 'Available'),
    ('critical', 'Critical'),
    ('assigned', 'Assigned'),
    ('late', 'Late'),
    ('revision', 'Revision'),
    ('disputed', 'Disputed'),
    ('completed', 'Completed'),
    ('approved', 'Approved'),
    ('cancelled', 'Cancelled'),
    ('archived', 'Archived'),
]

SPACING_CHOICES = [
    ('single', 'Single'),
    ('double', 'Double'),
]

FLAG_CHOICES = [
    ('UO', 'Urgent Order'),
    ('FCO', 'First Client Order'),
    ('HVO', 'High-Value Order'),
    ('PO', 'Preferred Order'),
    ('RCO', 'Returning Client Order'),
]


DISPUTE_STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_review', 'In Review'),
    ('resolved', 'Resolved'),
    ('escalated', 'Escalated'),
    ('closed', 'Closed'),
]


class Order(WebsiteSpecificBaseModel):
    """
    Represents an order placed by a client.
    Inherits from WebsiteSpecificBaseModel for multi-website compatibility.
    """
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders_as_client",
        null=True,
        blank=True,
        limit_choices_to={'role': 'client'},
        help_text="The client who placed this order. Leave blank for admin-created orders."
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders_as_writer",
        limit_choices_to={'role': 'writer'},
        help_text="The writer assigned to this order."
    )
    preferred_writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'writer'},
        help_text="Preferred writer for this order."
    )
    discount_code = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Discount code applied to this order."
    )
    writer_quality = models.ForeignKey(
        'pricing_configs.WriterQuality',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Selected writer quality level."
    )
    paper_type = models.ForeignKey(
        'order_configs.PaperType',
        on_delete=models.PROTECT,
        help_text="The type of paper requested."
    )
    topic = models.CharField(max_length=255, help_text="The topic or title of the order.")
    instructions = models.TextField(help_text="Detailed instructions for the order.")
    academic_level = models.ForeignKey(
        'pricing_configs.AcademicLevelPricing',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The academic level required."
    )
    formatting_style = models.ForeignKey(
        'order_configs.FormattingStyle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The formatting style required."
    )
    subject = models.ForeignKey(
        'order_configs.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The subject of the order."
    )
    type_of_work = models.ForeignKey(
        'order_configs.TypeOfWork',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The type of work requested."
    )
    english_type = models.ForeignKey(
        'order_configs.EnglishType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Preferred English style for the paper."
    )
    pages = models.PositiveIntegerField(help_text="Number of pages required.")
    slides = models.PositiveIntegerField(default=0, help_text="Number of slides.")
    resources = models.PositiveIntegerField(default=0, help_text="Number of references or sources.")
    spacing = models.CharField(
        max_length=10, choices=SPACING_CHOICES, default='double', help_text="Spacing for the order."
    )
    extra_services = models.ManyToManyField(
        'pricing_configs.AdditionalService',
        blank=True,
        related_name='orders',
        help_text="Additional services requested by the client or admin."
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', help_text="Current status of the order.")
    flag = models.CharField(
        max_length=3, choices=FLAG_CHOICES, null=True, blank=True, help_text="System-assigned or admin-set order flag."
    )
    deadline = models.DateTimeField(help_text="The deadline for the order.")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total cost of the order.")
    writer_compensation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Compensation for the writer.")
    writer_deadline = models.DateTimeField(null=True, blank=True, help_text="Writer's deadline.")
    is_paid = models.BooleanField(default=False, help_text="Indicates if the order is paid.")
    created_by_admin = models.BooleanField(default=False, help_text="Indicates if the order was created by an admin.")
    is_special_order = models.BooleanField(default=False, help_text="Indicates if this is a special order.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the order was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Date and time when the order was last updated.")

    # Include existing methods: calculate_total_cost, calculate_writer_compensation, assign_flags, etc.
    # *** To add the writer progress field ****
    def __str__(self):
        return f"Order #{self.id} - {self.topic} ({self.status})"
    

    class Meta:
        ordering = ['-created_at']


class WriterProgress(models.Model):
    """
    Tracks progress logs for writers working on orders.
    """
    writer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="progress_logs",
        limit_choices_to={"role": "writer"},
        help_text="The writer associated with this progress log."
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="progress_logs",
        help_text="The order associated with this progress log."
    )
    progress = models.PositiveIntegerField(help_text="Progress percentage (0-100).")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Progress {self.progress}% for Order {self.order.id} by {self.writer.username}"

class Dispute(WebsiteSpecificBaseModel):
    """
    Tracks disputes raised for an order.
    The order status is automatically updated when disputes are raised, reviewed, or resolved.
    """
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='disputes',
        help_text="The order associated with this dispute."
    )
    raised_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_raised',
        help_text="The user who raised the dispute (admin, client, editor, support, superadmin)."
    )
    status = models.CharField(
        max_length=20,
        choices=DISPUTE_STATUS_CHOICES,
        default='open',
        help_text="The current status of the dispute."
    )
    resolution_outcome = models.CharField(
        max_length=20,
        choices=[
            ('writer_wins', 'Writer Wins'),
            ('client_wins', 'Client Wins'),
            ('extend_deadline', 'Extend Deadline'),
            ('reassign', 'Reassign Order'),
        ],
        null=True,
        blank=True,
        help_text="Outcome of the dispute resolution."
    )
    reason = models.TextField(help_text="Reason for raising the dispute.")
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Notes or comments regarding the resolution of the dispute."
    )
    writer_responded = models.BooleanField(
        default=False,
        help_text="Indicates whether the writer has responded to the dispute."
    )
    admin_extended_deadline = models.DateTimeField(
        null=True, blank=True, help_text="If set, admin has manually extended the deadline."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the dispute was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the dispute was last updated.")

    def save(self, *args, **kwargs):
        """
        Automatically update order status when dispute is raised, reviewed, escalated, or resolved.
        """
        Order = apps.get_model('orders', 'Order')  # ✅ Lazy load Order model to avoid circular import

        if self._state.adding and self.order.status == 'cancelled':
            raise ValueError("Cannot raise a dispute for a cancelled order.")

        if self._state.adding:  # If this is a new dispute
            self.order.status = 'disputed'
            self.notify_users(
                "New Dispute Raised",
                f"A dispute has been raised for Order #{self.order.id}. Admin review is required."
            )

        if self.status == 'in_review':
            self.order.status = 'in_review'

        elif self.status == 'escalated':
            self.order.status = 'escalated'

        elif self.status == 'resolved':
            self.resolve_dispute_action()

        self.order.save()
        super().save(*args, **kwargs)

    def resolve_dispute_action(self):
        """
        Updates the order status based on the dispute resolution decision.
        """
        if self.resolution_outcome == 'writer_wins':
            self.order.status = 'completed'
        elif self.resolution_outcome == 'client_wins':
            self.order.status = 'cancelled'
        elif self.resolution_outcome == 'extend_deadline':
            self.order.status = 'revision'
        elif self.resolution_outcome == 'reassign':
            self.order.status = 'available'
            self.order.writer = None

        self.order.save()

    def notify_users(self, subject, message):
        recipients = []

        # Notify assigned writer
        if self.order.writer:
            recipients.append(self.order.writer.email)

        # Notify the person who raised the dispute
        if self.raised_by:
            recipients.append(self.raised_by.email)

        # Notify admins
        admin_emails = User.objects.filter(role__in=['admin', 'superadmin', 'support']).values_list('email', flat=True)
        recipients.extend(admin_emails)

        if recipients:
            send_mail(subject, message, "no-reply@yourdomain.com", recipients)


    def __str__(self):
        return f"Dispute #{self.id} for Order #{self.order.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class DisputeWriterResponse(models.Model):
    """
    Model to track writer responses to disputes.
    Writers must respond before a final decision.
    """
    dispute = models.ForeignKey(
        Dispute,
        on_delete=models.CASCADE,
        related_name='writer_responses',
        help_text="The dispute being responded to."
    )
    responded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dispute_writer_responses',
        limit_choices_to={'role': 'writer'},
        help_text="The writer responding to the dispute."
    )
    response_text = models.TextField(help_text="Writer's response or clarification.")
    response_file = models.FileField(
        upload_to='dispute_responses/', 
        null=True, 
        blank=True,
        help_text="Optional file upload for revised work."
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Time of response.")

    def __str__(self):
        return f"Writer Response for Dispute #{self.dispute.id} by {self.responded_by.username}"


    def save(self, *args, **kwargs):
        """Mark dispute as responded when a writer submits a response."""
        self.dispute.writer_responded = True
        self.dispute.save()
        super().save(*args, **kwargs)
    class Meta:
        unique_together = ('dispute', 'responded_by')
        ordering = ['-timestamp']



class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    date_processed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.status} - ${self.amount}"

    @classmethod
    def create_transaction(cls, order, transaction_id, amount, payment_method=""):
        """Create a new payment transaction"""
        return cls.objects.create(
            order=order,
            transaction_id=transaction_id,
            amount=amount,
            payment_method=payment_method,
            status="pending"
        )

    def mark_completed(self):
        """Mark the transaction as completed"""
        self.status = "completed"
        self.save()

    def mark_failed(self):
        """Mark the transaction as failed"""
        self.status = "failed"
        self.save()

    def refund(self):
        """Mark the transaction as refunded"""
        self.status = "refunded"
        self.save()