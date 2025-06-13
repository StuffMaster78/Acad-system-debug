from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from datetime import timedelta
from django.db import models
from django.utils import timezone

from core.celery import celery
# from websites.models import Website
from discounts.models.discount import Discount
from order_configs.models import WriterDeadlineConfig
from order_configs.models import AcademicLevel
from pricing_configs.models import PricingConfiguration
from django.core.exceptions import ValidationError

from .services.pricing_calculator import PricingCalculatorService
from django.apps import apps
from websites.models import Website
from orders.order_enums import (
    OrderStatus, OrderFlags,
    DisputeStatusEnum,
    SpacingOptions
)
from django.contrib.postgres.fields import ArrayField

User = settings.AUTH_USER_MODEL 

# # Use apps.get_model() to access Website model lazily
# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()

# from writer_management.models import wr
class Order(models.Model):
    """
    Represents an order placed by a client.
    Inherits from WebsiteSpecificBaseModel
    for multi-website compatibility.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order"
    )
    client = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="orders_as_client",
        null=True,
        blank=True,
        limit_choices_to={'role': 'client'},
        help_text=(
            "The client who placed this order."
            "Leave blank for admin-created orders."
        )
    )
    assigned_writer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders_as_writer",
        limit_choices_to={'role': 'writer'},
        help_text="The writer assigned to this order."
    )
    preferred_writer = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'writer'},
        help_text="Preferred writer for this order."
    )
    discount = models.ForeignKey(
        Discount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
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
    topic = models.CharField(
        max_length=255, 
        help_text=(
            "The topic or title of the order."
        )
    )
    order_instructions = models.TextField(
        help_text=(
            "Detailed instructions for the order."
        )
    )
    academic_level = models.ForeignKey(
        AcademicLevel,
        on_delete=models.PROTECT,
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
    is_follow_up = models.BooleanField(default=False)
    previous_order = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="follow_up_orders",
        help_text="Reference to the previous order this one follows up on."
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
    number_of_pages = models.PositiveIntegerField(
        help_text="Number of pages required."
    )
    number_of_slides = models.PositiveIntegerField(
        default=0, help_text="Number of slides."
    )
    number_of_refereces = models.PositiveIntegerField(
        default=0, help_text="Number of references or sources."
    )
    spacing = models.CharField(
        max_length=10,
        choices=SpacingOptions.choices(),
        default=SpacingOptions.SINGLE.value,
        help_text="Spacing for the order."
    )
    extra_services = models.ManyToManyField(
        'pricing_configs.AdditionalService',
        blank=True,
        related_name='orders',
        help_text="Additional services requested."
    )
    status = models.CharField(
        max_length=20,
        choices=[(status.value, status.name) for status in OrderStatus],
        default=OrderStatus.CREATED.value,
        help_text="Current status of the order."
    )
    flags = ArrayField(
        base_field=models.CharField(
            max_length=10,
            choices=OrderFlags.choices()
        ),
        default=list,
        blank=True,
        help_text="Flags related to the order (e.g., Urgent Order, Returning Client)."
    )
    client_deadline = models.DateTimeField(
        help_text="The deadline for the order."
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, blank=True,
        default=Decimal('0.00'),
        help_text="Total price of the order."
    )
    writer_compensation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal('0.00'),
        help_text="Compensation for the writer."
    )
    writer_deadline_percentage = models.ForeignKey(
        WriterDeadlineConfig,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The Deadline the Writer sees"
    )
    writer_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Writer's deadline."
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Indicates if the order is paid."
    )
    is_urgent = models.BooleanField(default=False)
    created_by_admin = models.BooleanField(
        default=False,
        help_text="Indicates if the order was created by an admin."
    )
    is_special_order = models.BooleanField(
        default=False,
        help_text="Indicates if this is a special order."
    )
    is_public = models.BooleanField(default=False)  # Open to any writer if true
    reassignment_requested = models.BooleanField(default=False)
    completed_by = models.ForeignKey(
        'users.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    completion_notes = models.TextField(null=True, blank=True)
    reassigned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="Date and time when the order was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the order was last updated."
    )

    # Include existing methods: calculate_total_cost,
    # calculate_writer_compensation, assign_flags, etc.
    # *** To add the writer progress field ****
    @property
    def status_enum(self) -> OrderStatus:
        """Get the order status as an `OrderStatus` enum.

        Returns:
            OrderStatus: The current status of the order as an enum.
        """
        return OrderStatus(self.status)

    @status_enum.setter
    def status_enum(self, value: OrderStatus):
        """Set the order status using an `OrderStatus` enum.

        Args:
            value (OrderStatus): The new status to assign to the order.

        Raises:
            ValueError: If `value` is not an instance of `OrderStatus`.
        """
        if isinstance(value, OrderStatus):
            self.status = value.value
        else:
            raise ValueError("status_enum must be an OrderStatus enum instance")

        
    def save(self, *args, **kwargs):
            """
            Trigger price recalculation whenever the order is saved.
            """
            self.total_cost = PricingCalculatorService.calculate_total_price(self)
            super(Order, self).save(*args, **kwargs)

    def update_total_price(self):
        """
        Calculates and updates the total price of the order.
        """
        self.total_price = PricingCalculatorService.calculate_total_price(self)
        self.save(update_fields=["total_price"])

    def calculate_writer_deadline(
            client_deadline,
            writer_deadline_percentage
    ):
        """
        Calculates the writer deadline based on client deadline
        and admin-set buffer (writer deadline) percentage.

        Args:
            client_deadline (datetime): The deadline the client sees.
            buffer_percentage (float): A value between 0 and 100 (e.g., 80 for 80%).

        Returns:
            datetime: The deadline the writer should aim for.
        """
        if not (0 < writer_deadline_percentage <= 100):
            raise ValueError("Buffer percentage must be between 0 and 100.")

        now = timezone.now()
        total_time = client_deadline - now

        if total_time.total_seconds() <= 0:
            raise ValueError("Client deadline must be in the future.")

        writer_time = total_time * (writer_deadline_percentage / 100)

        writer_deadline = now + writer_time
        return writer_deadline

    def apply_discount(self, discount_code):
        """Apply a discount to the order."""
        discount = Discount.objects.get(code=discount_code)

        if not discount.is_valid(self.user):
            raise ValidationError(
                "Discount is not valid for this order."
            )

        if discount.discount_type == 'percentage':
            discount_amount = (self.total_price * discount.value) / Decimal(100)
        else:  # Fixed amount
            discount_amount = discount.value

        new_total_price = self.total_price - discount_amount + self.additional_cost
        
        # Ensure new total price isn't negative
        if new_total_price < 0:
            raise ValidationError("Order total cannot be negative.")
        
    def update_status(self, new_status):
        """Update order status."""
        self.status = new_status
        self.save()


    def add_additional_cost(self, additional_amount):
        """Add additional costs (e.g., extra pages or slides)."""
        self.additional_cost += Decimal(additional_amount)
        self.save()

    def change_deadline(self, new_deadline):
        """Method for safely changing the deadline and logging it."""
        DeadlineChangeLog.objects.create(
            order=self,
            old_deadline=self.deadline,
            new_deadline=new_deadline,
            changed_by=self.client
        )
        self.deadline = new_deadline
        self.save()


    def update_status_based_on_payment(self):
        """
        Updates the order status when payment status
        changes in orders_payments_management.
        """
        Payment = apps.get_model(
            'orders_payments_management', 'OrderPayment'
        )
        payment = Payment.objects.filter(
            order=self
        ).order_by('-created_at').first()  # Ensure latest payment

        if payment:
            if payment.status == 'paid' and self.status == 'unpaid':
                self.status = 'pending'
                self.is_paid = True
            elif payment.status in ['failed', 'refunded']:
                self.status = 'cancelled'
                self.is_paid = False

            self.save()

    def mark_as_completed(self, user):
        """
        Marks the order as completed if a Final Draft is
        uploaded by an authorized user.
        Ensures only authorized users (staff, writers, editors, support)
        can complete an order.
        """
        allowed_roles = ["Writer", "Editor", "Support", "Admin", "Superadmin"]
        if user.is_staff or user.groups.filter(
            name__in=allowed_roles
            ).exists():
                self.status = "completed"
                self.save()

                # Send email notification asynchronously
                from orders.tasks import send_order_completion_email
                if self.client:
                    celery.current_app.send_task(
                    "orders.tasks.send_order_completion_email",
                    args=[self.client.email, self.client.username, self.id]
                )
                return True
        return False
    
    def add_pages(self, additional_pages: int):
        """
        Add extra pages to the existing order, recalculate the price for the new pages.
        The client will be redirected to pay for the extra pages.
        """
        self.number_of_pages += additional_pages
        # Recalculate the price with the new page count
        base_price = PricingCalculatorService.calculate_base_price(self)
        # Calculate price for the new pages
        new_page_price = additional_pages * PricingConfiguration.objects.first().base_price_per_page
        self.total_cost = base_price + new_page_price  # Update the total cost
        self.save()

    def add_slides(self, additional_slides: int):
        """
        Add extra slides to the existing order, recalculate the price for the new slides.
        The client will be redirected to pay for the extra slides.
        """
        self.number_of_slides += additional_slides
        # Recalculate price with new slide count
        base_price = PricingCalculatorService.calculate_base_price(self)
        new_slide_price = additional_slides * PricingConfiguration.objects.first().base_price_per_slide
        self.total_cost = base_price + new_slide_price  # Update the total cost
        self.save()

    def add_extra_service(self, service):
        """
        Add extra service to the order, recalculate price, and prompt for payment.
        """
        self.extra_services.add(service)
        self.total_cost = PricingCalculatorService.calculate_total_price(self)  # Recalculate price with new service
        self.save()

    def change_deadline(self, new_deadline):
        """
        Change the deadline, apply the necessary convenience fee if reduced.
        """
        pricing_config = PricingConfiguration.objects.first()
        old_deadline = self.deadline
        self.deadline = new_deadline

        if new_deadline < old_deadline:
            # Apply convenience fee if deadline is reduced
            self.total_cost += pricing_config.convenience_fee

        self.total_cost = PricingCalculatorService.calculate_total_price(self)  # Recalculate after changing deadline
        self.save()

    def add_discount(self, discount):
        """
        Add a discount to the order and recalculate the total price.
        """
        self.discount = discount
        self.total_cost = PricingCalculatorService.calculate_total_price(self)
        self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.topic} ({self.status})"

    class Meta:
        ordering = ['-created_at']

class PreferredWriterResponse(models.Model):
    """
    Handles the preferred writer's response when declining
    to work on an order.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='preferred_writer_decline_response'
    ) 
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(
        max_length=10,
        choices=[('accepted', 'Accepted'), ('declined', 'Declined')]
    )
    reason = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(auto_now_add=True)

class DeadlineChangeLog(models.Model):
    """
    Logs every deadline change for audit.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='deadline_change_log'
    ) 
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    old_deadline = models.DateTimeField()
    new_deadline = models.DateTimeField()
    changed_by = models.ForeignKey('User', on_delete=models.CASCADE)
    reason = models.TextField()

    def __str__(self):
        return f"Deadline changed for Order #{self.order.id}"

class WriterRequest(models.Model):
    """
    Model to track writer requests such as deadline extensions or page
    increases.
    """
    class RequestType(models.TextChoices):
        DEADLINE = 'deadline_extension', 'Deadline Extension'
        PAGES = 'page_increase', 'Page Increase'
        SLIDES = 'slide_increase', 'Slide Increase'

    class RequestStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_deadline_pages_request"
    )
    order = models.ForeignKey(
        'Order', on_delete=models.CASCADE,
        related_name="writer_requests"
    )
    request_type = models.CharField(
        max_length=50,
        choices=RequestType.choices
    )
    requested_by_writer = models.ForeignKey(
        'User', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    new_deadline = models.DateTimeField(
        null=True, blank=True
    )
    additional_pages = models.PositiveIntegerField(null=True, blank=True)
    additional_slides = models.PositiveIntegerField(null=True, blank=True)
    request_reason = models.TextField()
    client_approval = models.BooleanField(default=False)
    admin_approval = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        """
        Return a string representation of the request.
        Returns:
            str: A summary of the request, including order ID and type.
        """
        return f"WriterRequest({self.id}) - {self.request_type} for Order #{self.order.id}"

class WriterProgress(models.Model):
    """
    Tracks progress logs for writers working on orders.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_progress'
    )
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
    progress_percentage = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)]
    )
    text_description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional update details."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def progress(self):
        return f"{self.completed_tasks}/{self.total_tasks}"
    

    def update_progress(self, completed_tasks):
        """Update the progress based on completed tasks."""
        self.completed_tasks = completed_tasks
        self.progress_percentage = (completed_tasks / self.total_tasks) * 100
        self.save()
    
    class Meta:
            unique_together = ('writer', 'order', 'timestamp')
            ordering = ['-timestamp']

    def __str__(self):
        return (
            f"Progress {self.progress_percentage}% for Order {self.order.id} "
            f"by {self.writer.username}"
        )


class Dispute(models.Model):
    """
    Tracks disputes raised for an order.
    The order status is automatically updated when 
    disputes are raised, reviewed, or resolved.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_dispute'
    )
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
        help_text="The user who raised the dispute."
    )
    dispute_status = models.CharField(
        max_length=20,
        choices=DisputeStatusEnum.choices(),
        default=DisputeStatusEnum.OPEN.value,
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
    reason = models.TextField(
        help_text="Reason for raising the dispute."
    )
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Notes or comments regarding the resolution."
    )
    writer_responded = models.BooleanField(
        default=False,
        help_text="Indicates whether the writer has responded."
    )
    admin_extended_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If set, admin has manually extended the deadline."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the dispute was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the dispute was last updated."
    )

    def save(self, *args, **kwargs):
        """
        Automatically update order status when dispute is
        raised, reviewed, escalated, or resolved.
        """
        Order = apps.get_model('orders', 'Order')

        if self._state.adding and self.order.status == 'cancelled':
            raise ValueError(
                "Cannot raise a dispute for a cancelled order."
            )
        if self._state.adding and self.order.status == 'progress':
            raise ValueError(
                "Cannot raise a dispute for an order in progress."
            )

        if self._state.adding:
            self.order.status = 'disputed'
            self.writer_responded = False
            self.notify_users(
                "New Dispute Raised",
                f"A dispute has been raised for Order #{self.order.id}. "
                "Admin review is required."
            )
        if self.status == 'in_review':
            self.order.status = 'in_review'
        elif self.status == 'escalated':
            self.order.status = 'escalated'
        elif self.status == 'resolved':
            self.resolve_dispute_action()

        self.order.save()
        super().save(*args, **kwargs)

    def resolve_dispute_action(self, resolved_by):
        """
        Updates the order status based on
        the dispute resolution decision.
        """
        if self.resolution_outcome == 'writer_wins':
            self.order.status = 'completed'
        elif self.resolution_outcome == 'client_wins':
            self.order.status = 'cancelled'
        elif self.resolution_outcome == 'extend_deadline':
            self.order.change_deadline(resolved_by.new_deadline)
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
        admin_emails = User.objects.filter(
            role__in=['admin', 'superadmin', 'support']
        ).values_list('email', flat=True)

        if recipients:
            send_mail(
                subject,
                message, 
                "no-reply@yourdomain.com",
                recipients
            )

    def __str__(self):
        return f"Dispute #{self.id} for Order #{self.order.id} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class DisputeWriterResponse(models.Model):
    """
    Model to track writer responses to disputes.
    Writers must respond before a final decision.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='dispute_writer_response'
    )
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
    response_text = models.TextField(
        help_text="Writer's response or clarification."
    )
    response_file = models.FileField(
        upload_to='dispute_responses/',
        null=True,
        blank=True,
        help_text="Optional file upload for revised work."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time of response."
    )

    def __str__(self):
        return (
            f"Writer Response for Dispute #{self.dispute.id} by "
            f"{self.responded_by.username}"
        )


    def save(self, *args, **kwargs):
        """
        Mark dispute as responded
        when a writer submits a response.
        """
        self.dispute.writer_responded = True
        self.dispute.save()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('dispute', 'responded_by')
        ordering = ['-timestamp']


class ReassignmentRequest(models.Model):
    """
    Handles reassignment requests by client or writer.
    Also handles force-reassign by admin.
    """
    REQUESTED_BY_CHOICES = (
        ('client', 'Client'),
        ('writer', 'Writer'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),    # e.g. admin approved but not reassigned yet
        ('rejected', 'Rejected'),
        ('reassigned', 'Reassigned'),  # actioned
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reassignment_requests'
    )

    requested_by = models.CharField(
        max_length=10,
        choices=REQUESTED_BY_CHOICES,
        help_text="Whether the client or writer requested this reassignment."
    )

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reassignment_requests_made',
        help_text="The actual user who made the request."
    )
    admin_initiated = models.BooleanField(
        default=False,
        help_text="Was this reassignment initiated by admin?"
    )
    reason = models.TextField(
        help_text="The reason for requesting reassignment."
    )

    preferred_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_reassignments',
        help_text="Optional preferred writer requested by the client."
    )

    fine_applied = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        help_text="Fine applied to writer if they requested reassignment near deadline."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of the reassignment request."
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reassignment_requests_processed',
        help_text="Admin or system user who processed this request."
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional field for system flags, debug info, auto-approved flags, etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag."
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ReassignmentRequest(Order #{self.order_id}, {self.requested_by}, {self.status})"

    def soft_delete_request(request_id):
        req = ReassignmentRequest.objects.get(id=request_id)
        req.is_deleted = True
        req.save()
    def is_fine_needed(self, threshold=0.8):
        from orders.services.reassignment import is_near_deadline
        return is_near_deadline(self.order, threshold)

    def apply_default_fine(self, percentage=0.10):
        from orders.services.reassignment import calculate_fine
        self.fine_applied = calculate_fine(self.order, percentage)
        self.save()

    def mark_resolved(self, status, fine=0.00, processed_by=None, metadata=None):
        self.status = status
        self.fine_applied = fine
        self.resolved_at = timezone.now()
        if processed_by:
            self.processed_by = processed_by
        if metadata:
            self.metadata = metadata
        self.save()


class OrderDiscount(models.Model):
    """
    Tracks which discounts were applied to a specific order and their amounts.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="applied_discounts"
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.discount.code} - ${self.amount} on Order {self.order.id}"