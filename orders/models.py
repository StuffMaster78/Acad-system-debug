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


from django.db import models
from django.utils.timezone import now
from users.models import User
from core.models.base import WebsiteSpecificBaseModel

DISPUTE_STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_review', 'In Review'),
    ('resolved', 'Resolved'),
    ('escalated', 'Escalated'),
    ('closed', 'Closed'),
]


class Dispute(WebsiteSpecificBaseModel):
    """
    Model to track disputes raised for an order.
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
        help_text="The user who raised the dispute (client, writer, or admin)."
    )
    status = models.CharField(
        max_length=20,
        choices=DISPUTE_STATUS_CHOICES,
        default='open',
        help_text="The current status of the dispute."
    )
    reason = models.TextField(help_text="Reason for raising the dispute.")
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Notes or comments regarding the resolution of the dispute."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the dispute was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the dispute was last updated.")

    def resolve(self, resolution_notes=None):
        """
        Resolve the dispute.
        """
        self.status = 'resolved'
        self.resolution_notes = resolution_notes
        self.save()

    def escalate(self, resolution_notes=None):
        """
        Escalate the dispute.
        """
        self.status = 'escalated'
        self.resolution_notes = resolution_notes
        self.save()

    def close(self, resolution_notes=None):
        """
        Close the dispute.
        """
        self.status = 'closed'
        self.resolution_notes = resolution_notes
        self.save()

    def __str__(self):
        return f"Dispute #{self.id} for Order #{self.order.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']